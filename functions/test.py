import os
import sys
import importlib
import argparse

sys.path.append('../APDrawingGAN/')
sys.path.append('../APDrawingGAN/models')
sys.path.append('..')
utilhtml = importlib.import_module('APDrawingGAN.util.html')
utilvisualizer = importlib.import_module('APDrawingGAN.util.visualizer')
apdata = importlib.import_module('APDrawingGAN.data')
optionstest = importlib.import_module('APDrawingGAN.options.test_options')
apmodel = importlib.import_module('APDrawingGAN.models')

class Options(optionstest.TestOptions):
    def __init__(self,parser):
        self.parser = parser
        super().initialize(self.parser)

    def gather_options(self):
        # initialize parser with basic options
        if not self.initialized:
            parser = argparse.ArgumentParser(
                formatter_class=argparse.ArgumentDefaultsHelpFormatter)
            parser = self.initialize(parser)
        else:
            parser = self.parser

        # get the basic options
        opt, _ = parser.parse_known_args()

        # modify model-related parser options
        model_name = opt.model
        model_option_setter = apmodel.get_option_setter(model_name)
        parser = model_option_setter(parser, self.isTrain)
        opt, _ = parser.parse_known_args()  # parse again with the new defaults

        # modify dataset-related parser options
        dataset_name = opt.dataset_mode
        dataset_option_setter = apdata.get_option_setter(dataset_name)
        parser = dataset_option_setter(parser, self.isTrain)

        self.parser = parser

        return parser.parse_args()

def remove_option(parser, arg):
    for action in parser._actions:
        if (vars(action)['option_strings']
            and vars(action)['option_strings'][0] == arg) \
                or vars(action)['dest'] == arg:
            parser._remove_action(action)

    for action in parser._action_groups:
        vars_action = vars(action)
        var_group_actions = vars_action['_group_actions']
        for x in var_group_actions:
            if x.dest == arg:
                var_group_actions.remove(x)
                return

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    opt = Options(parser)
    remove_option(opt.parser,'dataroot')

    print(opt.parser.parse_args())
    opt.parser.set_defaults(dataroot='detect_result', name='formal_author',checkpoints_dir='../checkpoints',
                            model='test', dataset_mode='single', norm='batch', which_epoch=300, gpu_ids='-1')
    print(opt.parser.parse_args())
    opt = opt.parse()
    opt.use_local = True
    opt.num_threads = 1   # test code only supports num_threads = 1
    opt.batch_size = 1  # test code only supports batch_size = 1
    opt.serial_batches = True  # no shuffle
    opt.no_flip = True  # no flip
    opt.display_id = -1  # no visdom display
    data_loader = apdata.CreateDataLoader(opt)
    dataset = data_loader.load_data()
    model = apmodel.create_model(opt)
    model.setup(opt)
    # create website
    web_dir = os.path.join(opt.results_dir, opt.name,
                           '%s_%s' % (opt.phase, opt.which_epoch))
    webpage = utilhtml.HTML(web_dir, 'Experiment = %s, Phase = %s, Epoch = %s' % (
        opt.name, opt.phase, opt.which_epoch))
    # test
    for i, data in enumerate(dataset):
        if i >= opt.how_many:  # test code only supports batch_size = 1, how_many means how many test images to run
            break
        model.set_input(data)
        model.test()
        # in test the loadSize is set to the same as fineSize
        visuals = model.get_current_visuals()
        img_path = model.get_image_paths()
        if i % 5 == 0:
            print('processing (%04d)-th image... %s' % (i, img_path))
        utilvisualizer.save_images(
            webpage, visuals, img_path, aspect_ratio=opt.aspect_ratio, width=opt.display_winsize)

    webpage.save()
