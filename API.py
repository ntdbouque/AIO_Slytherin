import gradio as gr
import os
import glob
from model import QWenVL
import json
import cv2


# MODEL
model = QWenVL()

os.environ["GRADIO_TEMP_DIR"] = os.path.join(os.getcwd(), "tmp")
dataset_path = '/workspace/competitions/1AngleHackathon/data/dataset'



def show_bbox(info_dct):
    image_path = info_dct['Image Path']
    image = cv2.imread(image_path)
    image = cv2.resize(image, (1000,1000))
    print('img path:', image_path)
    
    if info_dct['Location'] == 'grocery store' or info_dct['Location'] == 'supermarket':
        label_billboard = ''
        bbox_billboard = []
        
        label_fridge = ''
        bbox_fridge = []
        
        label_stack = ''
        bbox_stack = []
        
        for idx, (key, value) in enumerate(info_dct.items(), 0):
            if idx == 3:
                label_billboard = key
                bbox_billboard = value
            elif idx == 5:
                label_fridge = key
                bbox_fridge = value
            elif idx == 7:
                label_stack = key
                bbox_stack = value
    
        for box in bbox_billboard:
            x_tl, y_tl, x_br, y_br = map(int, box) 
               
            cv2.rectangle(image, (x_tl, y_tl), (x_br, y_br), (255, 0 , 0), 2)
            cv2.putText(image, label_billboard, (x_tl, y_tl - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
          
          
        for box in bbox_fridge:
            x_tl, y_tl, x_br, y_br = map(int, box)    
            cv2.rectangle(image, (x_tl, y_tl), (x_br, y_br), (0, 255 , 0), 2)
            cv2.putText(image, label_fridge, (x_tl, y_tl - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2) 
            
        for box in bbox_stack:
            x_tl, y_tl, x_br, y_br = map(int, box)    
            cv2.rectangle(image, (x_tl, y_tl), (x_br, y_br), (0, 0 , 255), 2)
            cv2.putText(image, label_stack, (x_tl, y_tl - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2) 
            
    elif info_dct['Location'] == 'restaurant':
        label_customer = ''
        bbox_customer = []
        
        label_staff = ''
        bbox_staff = []
        
        for idx, (key, value) in enumerate(info_dct.items(), 0):
            if idx == 5:
                label_customer = key
                bbox_customer = value
            elif idx == 7:
                label_staff = key
                bbox_staff = value
                
        for box in bbox_customer:
           
            x_tl, y_tl, x_br, y_br = map(int, box)    
            cv2.rectangle(image, (x_tl, y_tl), (x_br, y_br), (255, 0 , 0), 2)
            cv2.putText(image, label_customer, (x_tl, y_tl - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
          
        for box in bbox_staff:
            x_tl, y_tl, x_br, y_br = map(int, box)    
            cv2.rectangle(image, (x_tl, y_tl), (x_br, y_br), (0, 255 , 0), 2)
            cv2.putText(image, label_staff, (x_tl, y_tl - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2) 
        
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

def get_information(image_path, restaurant, grocery):
    image_path = os.path.join(dataset_path, image_path)
    info_dct = model.answer(image_path) 
    image = show_bbox(info_dct)
    return info_dct, image
    
def get_base_img_name(lst_img_paths):
    new_lst = []
    for img_path in lst_img_paths:
        img_path = os.path.basename(img_path)
        new_lst.append(img_path)
    return new_lst

def show_image(image_name):
    full_img_path = os.path.join(dataset_path, str(image_name))
    return full_img_path


dataset_path = '/workspace/competitions/1AngleHackathon/data/dataset'

lst_img_paths = sorted(glob.glob(os.path.join(dataset_path, '*.jpg')))
lst_img_paths = get_base_img_name(lst_img_paths)


### GRADIO BLOCK:

with gr.Blocks() as app:
    with gr.Tab('Demo'):
        with gr.Row():
            with gr.Column():
                input_text = gr.Dropdown(lst_img_paths, label = 'Images Name Selection')
                input_image = gr.Image()
                
                input_text.change(show_image, input_text, input_image)
                
                submit_btn = gr.Button("Submit")
            
            with gr.Column():
                show_output_text = gr.TextArea(label='Result')
                
                
                
                
                show_output_img = gr.Image(width=1000, height=1000)
    
            submit_btn.click(get_information, inputs=input_text, outputs=[show_output_text, show_output_img])
    with gr.Tab('Analysis'):
        with gr.Row():
            with gr.Column(scale = 0):
                plot_dropdown = gr.Dropdown(['Bar Chart', 'Pie Chart'], label = 'Type Graph')
                visualize_btn = gr.Button(value='Show Graph', size = 'sm')   
            plot = gr.Plot(scale = 2)
            
        #visualize_btn.click(fn=visualize, inputs = [], outputs = plot)

    
    app.launch()