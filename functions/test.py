import os
import sys
import importlib
sys.path.append('../APDrawingGAN/')

utilhtml = importlib.import_module('APDrawingGAN.util.html')
utilvisualizer = importlib.import_module('APDrawingGAN.util.visualizer')
apdata = importlib.import_module('APDrawingGAN.data')
optionstest = importlib.import_module('APDrawingGAN.options.test_options')
apmodel = importlib.import_module('APDrawingGAN.models')


if __name__ == '__main__':
    opt = optionstest.TestOptions()
    opt.parser.set_defaults(dataroot='functions/detect_result', name='formal_author',
                            model='test', dataset_mode='single', norm='batch', which_epoch=300, gpu_ids=-1)
    opt = opt.parse()
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
