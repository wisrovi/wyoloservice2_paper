from PIL import Image, ImageDraw, ImageFont
import os

def create_pipeline_image(path):
    img = Image.new('RGB', (800, 300), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    
    boxes = [
        ("COCO128\nDataset\n(N=128)", 50, 100),
        ("YOLO\nInference", 250, 100),
        ("Bootstrap\n(B=1000)", 450, 100),
        ("Statistical\nSignificance", 650, 100)
    ]
    
    for i, (text, x, y) in enumerate(boxes):
        # Draw box
        d.rectangle([x, y, x+120, y+100], fill=(200, 220, 255), outline=(0, 0, 0), width=2)
        # Draw text
        d.text((x+10, y+20), text, fill=(0, 0, 0))
        
        # Draw arrow
        if i < len(boxes) - 1:
            d.line([x+120, y+50, x+180, y+50], fill=(0,0,0), width=3)
            d.polygon([(x+180, y+50), (x+170, y+45), (x+170, y+55)], fill=(0,0,0))
            
    img.save(path)

if __name__ == '__main__':
    create_pipeline_image('/home/william.rodriguez/Documents/w_libraries/train_service2/wyoloservice2_paper/normal_papers/paper_5_statistical/en/pipeline.png')
    create_pipeline_image('/home/william.rodriguez/Documents/w_libraries/train_service2/wyoloservice2_paper/normal_papers/paper_5_statistical/es/pipeline.png')
