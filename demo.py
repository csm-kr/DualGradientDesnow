import os
import time
import torch
from config import device
from utils import  tensor2im, save_image
from gradient_sam import create_gradient_masks
from libtiff import TIFF
from PIL import Image
import torchvision.transforms.functional as F
from model import Dual_Grad_Desnow_Net, VGG


def demo(data_path, model, cls_model):
    """
    test dual gradient desnowing
    :param data_path: path of demo
    :param model: model for desnowing
    :param cls_model: model for classification
    :return: -
    """

    # ------------------- load -------------------
    tic = time.time()
    print('Demo...')

    img_list = os.listdir(data_path)

    # snow100k weight
    state_dict = torch.load('./models/snow100k_model_params.pth', map_location=device)
    cls_state_dict = torch.load('./models/snow100k_classification_vgg_16.pth', map_location=device)

    # srrs weight
    # state_dict = torch.load('./models/srrs_model_params.pth', map_location=device)
    # cls_state_dict = torch.load('./models/srrs_classification_vgg_16.pth', map_location=device)

    model.load_state_dict(state_dict, strict=True)
    model.eval()
    cls_model.load_state_dict(cls_state_dict, strict=True)
    cls_model.eval()

    for i, img_name in enumerate(img_list):
        print(i, "/", len(img_list))
        img_path = os.path.join(data_path, img_name)

        # load images
        if os.path.basename(img_path).split('.')[-1] == 'tif':
            # load tif image
            tif = TIFF.open(img_path)
            img_rgb = tif.read_image()
            snow_images = Image.fromarray(img_rgb).convert('RGB')

        else:
            # load jpg png img
            snow_images = Image.open(img_path).convert('RGB')

        snow_images = F.to_tensor(snow_images).unsqueeze(0)  # conver to batch 1
        snow_images = snow_images.to(device)
        grad_masks = create_gradient_masks(snow_images, cls_model)
        with torch.no_grad():
            output = model.eval()(snow_images, grad_masks)  # output : (a, _, _)
        desnow = output[0]

        if not os.path.isdir('./demo'):
            os.mkdir('./demo')
        desnow = tensor2im(desnow)
        # mask = tensor2im(mask)
        img_name = img_name.split('.')[0]
        save_image(desnow, './demo/' + 'desnow_' + img_name + '.png')  # for img_name is tuple


if __name__ == '__main__':
    # demo path FIXME
    deme_path = './real_snow_img'

    # model
    model = Dual_Grad_Desnow_Net().to(device)
    cls_model = VGG().to(device)

    # test
    demo(data_path=deme_path,
         model=model,
         cls_model=cls_model)



