'''
- Input: nhận vào 1 đường dẫn đến ảnh
- Output: thực hiện truy vấn với LLM, kết quả là một đoạn text chưa được rút trích thông tin

Thứ tự đi Prompt: location -> res/gro -> general
'''

from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.generation import GenerationConfig
import torch
torch.manual_seed(1234)
from extract_from_response import *
import json
import glob




class QWenVL():
    def __init__(self, precision = 'bf16'):
        self.location_prompt_path = '/workspace/competitions/1AngleHackathon/source/API/Prompt/Location.txt'
        self.restaurant_prompt_path = '/workspace/competitions/1AngleHackathon/source/API/Prompt/Restaurant_task.txt'
        self.grocery_prompt_path = '/workspace/competitions/1AngleHackathon/source/API/Prompt/Grocery_task.txt'
        self.context_prompt_path = '/workspace/competitions/1AngleHackathon/source/API/Prompt/Context.txt'
        
        self.tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen-VL-Chat", trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen-VL-Chat", device_map="cuda", trust_remote_code=True, **{precision: True}).eval()
        self.model.generation_config = GenerationConfig.from_pretrained("Qwen/Qwen-VL-Chat", trust_remote_code=True)
        
        self.info_dct = {}
        self.log_path = '/workspace/competitions/1AngleHackathon/source/API/log.json'
        self.lst_material = ['/workspace/competitions/1AngleHackathon/source/API/Materials/Billboard1.png', '/workspace/competitions/1AngleHackathon/source/API/Materials/Fridge.png', '/workspace/competitions/1AngleHackathon/source/API/Materials/stack.png']

    
    def replace_placeholder(self, text, replacement):
        return text.replace('__', replacement)
    
    
    def read_prompt(self, prompt_path):
        prompt_dct = {}
        with open(prompt_path, 'r') as txt:
            lines = txt.readlines()
            for line in lines:
                key = line.split('/ ')[0]
                value = line.split('/')[-1] 
                prompt_dct[key] = value
        return prompt_dct
            
    def response_context(self, his):
        context_prompt_dct = self.read_prompt(self.context_prompt_path)
        for type, content in context_prompt_dct.items():
            query = self.tokenizer.from_list_format([
                {'text': f'{content}'}
            ])
            response, history = self.model.chat(self.tokenizer, query = query, history = his)   
        return response, history
    
    def answer(self, image_path=None):
        print('NEW PROMPT:', image_path)
        
        # Restart new chat:
        self.info_dct = {}
        
        self.info_dct['Image Path'] = image_path
        
        history = None
        
        # LOCATION:
        location_prompt_dct = self.read_prompt(self.location_prompt_path)
        for type, content in location_prompt_dct.items():
            query = self.tokenizer.from_list_format([
                            {'image': f'{image_path}'},
                            {'text': f'{content}'},
                    ])
            response, history = self.model.chat(self.tokenizer, query = query, history = history)   
            
        # EXTRACT LOCATION:
        location = extract_location(response)
        self.info_dct['Location'] = location

        # CONTEXT:
       
        response, history = self.response_context(history)
    
        # TASK:
        if location == 'grocery store' or location == 'supermarket':
            grocery_prompt_dct = self.read_prompt(self.grocery_prompt_path)
        
            for type, content in grocery_prompt_dct.items():
                query = self.tokenizer.from_list_format([
                            {'image': f'{image_path}'},
                            {'text': f'{content}'},
                    ])
                response, history = self.model.chat(self.tokenizer, query = query, history = history)
        
                    
                print('type:', type)       
                print('response:', response)
                print('history:', history)
                print('##########################')
                
                
                if 'draw' in type:
                    # clear history:
                    history = None
                    _, history = self.response_context(history)
                    
                # EXTRACT GROCERY/SUPERMARKET     
                key, value = extract_grocery(image_path, type, response)
                self.info_dct[key] = value

        elif location == 'restaurant':
            restaurant_prompt_dct = self.read_prompt(self.restaurant_prompt_path)
            
            for type, content in restaurant_prompt_dct.items():
                
                if type == 'Res 4 draw':
                    content = self.replace_placeholder(content, str(self.info_dct['Number of customers in the picture']))
                elif type == 'Res 6 draw':
                    content = self.replace_placeholder(content, str(self.info_dct['Number of people in the picture'] - self.info_dct['Number of customers in the picture']))
                
                
                query = self.tokenizer.from_list_format([
                            {'image': f'{image_path}'},
                            {'text': f'{content}'},
                    ])    
                response, history = self.model.chat(self.tokenizer, query = query, history = history)  
              
                print('type:', type)
                print('response:', response)
                print('history', history)
                print('##########################')
                
                
                if 'draw' in type:
                    # clear history:
                    history = None
                    _, history = self.response_context(history)
                    
                    
                # EXTRACT RESTAURANT:
                key, value = extract_restaurant(image_path, type, response)
                self.info_dct[key] = value
        else:
            print('No Location for prompting')
            return 
        
        return self.info_dct
    
    
# if __name__ == '__main__':
#     model = QWenVL()
#     info_dct = model.answer('/workspace/competitions/1AngleHackathon/data/dataset/0018.jpg')
    



