import re
import os
import cv2
import pybboxes as pbx
from PIL import Image, ImageDraw

DES_FOLDER = '/workspace/competitions/1AngleHackathon/result/eval'

def draw_bounding_box(image_path, content, boxes):
    image = cv2.imread(image_path)
    image = cv2.resize(image, (1000,1000))
    
    for box in boxes:
        x_tl, y_tl, x_br, y_br = map(int, box)    
        cv2.rectangle(image, (x_tl, y_tl), (x_br, y_br), (255, 0 , 0), 2)
        cv2.putText(image, content, (x_tl, y_tl - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
    
    return image

def save_image(image, image_des_path):
    cv2.imwrite(image_des_path, image)

# Extract Location information:
def extract_location(response):
    location = response.split(': ')[-1]
    return location

# Extract informatin relevant to Restaurant: 
def extract_restaurant(image_path, type, response):
    if type == 'Res 1':
        atmosphere = response.split(':')[-1]
        return 'Emotion:', atmosphere
    
    
    elif type == 'Res 2':
        match = re.search(r'\d+', response)
        if match:
            num_people = int(match.group())
        else:
            print('Cannot extract')  
    
        return 'Number of people in the picture', num_people
    
    elif type == 'Res 3':
        match = re.search(r'\d+', response)
        if match:
            num_people = int(match.group())
        else:
            print('Cannot extract')  
    
        return 'Number of customers in the picture', num_people
    
    elif type == 'Res 5':
        match = re.search(r'\d+', response)
        if match:
            num_people = int(match.group())
        else:
            print('Cannot extract')  
    
        return 'Number of promotional staffs in the picture', num_people
    
    elif 'draw' in type:
        ref_match = re.search(r'<ref>(.*?)</ref>', response)
        if ref_match:
            ref_content = ref_match.group(1)
        else:
            ref_content = '<None>'

        pattern = r'<box>(.*?)</box>'
        
        matches = re.findall(pattern, response)
        
        bboxes = []
        
        for match in matches:
            coords = re.findall(r"\((\d+,\d+)\)", match)
            bboxes.append(coords)
            
        converted_data = []
        
        for box in bboxes:
            int_coords = []
            for coord in box:
                int_coords.extend(map(int, coord.split(',')))
            converted_data.append(int_coords)
        
        print('BBoxes:', converted_data)


        print('Ref Content:', ref_content)
        print('Boxes:', converted_data)
        
        return ref_content, converted_data

        image_name = os.path.basename(image_path)
        image_des_path = os.path.join(DES_FOLDER, image_name)
        
        image = draw_bounding_box(image_path, ref_content, converted_data)
        save_image(image, image_des_path)
        

    return a, b


# Extract information relevant to grocery store:
def extract_grocery(image_path, type, response):
    if type == 'Gro 1':
        yn = response.split(':')[-1]
        return 'is there a billboard', yn
        
    elif type == 'Gro 3':
        yn = response.split(':')[-1]
        return 'is there a refrigerator', yn
    
    elif type == 'Gro 5':
        yn = response.split(':')[-1]
        return 'is there a stack of beer crate', yn
    
    elif 'draw' in type:
        ref_match = re.search(r'<ref>(.*?)</ref>', response)
        if ref_match:
            ref_content = ref_match.group(1)
        else:
            ref_content = '<None>'

        pattern = r'<box>(.*?)</box>'
        
        matches = re.findall(pattern, response)
        
        bboxes = []
        
        for match in matches:
            coords = re.findall(r"\((\d+,\d+)\)", match)
            bboxes.append(coords)
            
        converted_data = []
        
        for box in bboxes:
            int_coords = []
            for coord in box:
                int_coords.extend(map(int, coord.split(',')))
            converted_data.append(int_coords)
        
        print('Ref Content:', ref_content)
        print('Boxes:', converted_data)
        
        return ref_content, converted_data
        
        image_name = os.path.basename(image_path)
        image_des_path = os.path.join(DES_FOLDER, image_name)
        
        image = draw_bounding_box(image_path, ref_content, converted_data)
        save_image(image, image_des_path)
    
    return a,b


if __name__ == '__main__':
    a, b = extract_grocery('/workspace/competitions/1AngleHackathon/data/dataset/0014.jpg', 'draw', '<ref>customers</ref><box>(720,3),(999,358)</box><box>(785,335),(1000,674)</box>')