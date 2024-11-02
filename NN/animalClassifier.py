import numpy as np
import torch
from torchvision import transforms
from PIL import Image
import torchvision.models as models
import torch.nn as nn

class AnimalClassifier:
    def __init__(self):
        # Define the model architecture
        self.model = models.mobilenet_v2(pretrained=False)
        self.model.classifier[1] = nn.Linear(self.model.classifier[1].in_features, 90)  # Adjust num_classes if needed

        # Load the saved state dictionary
        self.model.load_state_dict(torch.load('NN/animal_model.pth'))

        # Set the model to evaluation mode
        self.model.eval()
        self.animals = [
            'antelope', 'badger', 'bat', 'bear', 'bee', 
            'beetle', 'bison', 'boar', 'butterfly', 'cat', 
            'caterpillar', 'chimpanzee', 'cockroach', 'cow', 
            'coyote', 'crab', 'crow', 'deer', 'dog', 
            'dolphin', 'donkey', 'dragonfly', 'duck', 
            'eagle', 'elephant', 'flamingo', 'fly', 
            'fox', 'goat', 'goldfish', 'goose', 
            'gorilla', 'grasshopper', 'hamster', 'hare', 
            'hedgehog', 'hippopotamus', 'hornbill', 'horse', 
            'hummingbird', 'hyena', 'jellyfish', 'kangaroo', 
            'koala', 'ladybugs', 'leopard', 'lion', 
            'lizard', 'lobster', 'mosquito', 'moth', 
            'mouse', 'octopus', 'okapi', 'orangutan', 
            'otter', 'owl', 'ox', 'oyster', 'panda', 
            'parrot', 'pelecaniformes', 'penguin', 'pig', 
            'pigeon', 'porcupine', 'possum', 'raccoon', 
            'rat', 'reindeer', 'rhinoceros', 'sandpiper', 
            'seahorse', 'seal', 'shark', 'sheep', 
            'snake', 'sparrow', 'squid', 'squirrel', 
            'starfish', 'swan', 'tiger', 'turkey', 
            'turtle', 'whale', 'wolf', 'wombat', 
            'woodpecker', 'zebra'
        ]
        self.butterfly_species = [
            'SOUTHERN DOGFACE', 'ADONIS', 'BROWN SIPROETA', 'MONARCH',
            'GREEN CELLED CATTLEHEART', 'CAIRNS BIRDWING', 'EASTERN DAPPLE WHITE',
            'RED POSTMAN', 'MANGROVE SKIPPER', 'BLACK HAIRSTREAK', 'CABBAGE WHITE',
            'RED ADMIRAL', 'PAINTED LADY', 'PAPER KITE', 'SOOTYWING', 'PINE WHITE',
            'PEACOCK', 'CHECQUERED SKIPPER', 'JULIA', 'COMMON WOOD-NYMPH', 'BLUE MORPHO',
            'CLOUDED SULPHUR', 'STRAITED QUEEN', 'ORANGE OAKLEAF', 'PURPLISH COPPER',
            'ATALA', 'IPHICLUS SISTER', 'DANAID EGGFLY', 'LARGE MARBLE',
            'PIPEVINE SWALLOW', 'BLUE SPOTTED CROW', 'RED CRACKER', 'QUESTION MARK',
            'CRIMSON PATCH', 'BANDED PEACOCK', 'SCARCE SWALLOW', 'COPPER TAIL',
            'GREAT JAY', 'INDRA SWALLOW', 'VICEROY', 'MALACHITE', 'APPOLLO',
            'TWO BARRED FLASHER', 'MOURNING CLOAK', 'TROPICAL LEAFWING', 'POPINJAY',
            'ORANGE TIP', 'GOLD BANDED', 'BECKERS WHITE', 'RED SPOTTED PURPLE',
            'MILBERTS TORTOISESHELL', 'SILVER SPOT SKIPPER', 'AMERICAN SNOOT', 'AN 88',
            'ULYSES', 'COMMON BANDED AWL', 'CRECENT', 'METALMARK', 'SLEEPY ORANGE',
            'PURPLE HAIRSTREAK', 'ELBOWED PIERROT', 'GREAT EGGFLY', 'ORCHARD SWALLOW',
            'ZEBRA LONG WING', 'WOOD SATYR', 'MESTRA', 'EASTERN PINE ELFIN',
            'EASTERN COMA', 'YELLOW SWALLOW TAIL', 'CLEOPATRA', 'GREY HAIRSTREAK',
            'BANDED ORANGE HELICONIAN', 'AFRICAN GIANT SWALLOWTAIL', 'CHESTNUT',
            'CLODIUS PARNASSIAN'
        ]

    def transform_image__(self, image):
        transform = transforms.Compose([
            transforms.Resize((128, 128)),
            transforms.ToTensor()
        ])
        return transform(image)

    def classify(self, image_path):
        # Load the image
        image = Image.open(image_path)
        # Preprocess the image
        image = self.transform_image__(image)

        # Add a batch dimension
        image = image.unsqueeze(0)

        print(image.shape)

        # Make a prediction
        prediction = self.model(image)
        prediction = prediction.detach().numpy()
        predicted_class = np.argmax(prediction[0])
        predicted_animal = self.animals[predicted_class]


        # In reality we would have a separate model for each species
        predicted_species = "Unknown"
        if predicted_animal == 'butterfly':
            # Define the butterfly species model architecture
            butterfly_model = models.mobilenet_v2(pretrained=False)
            butterfly_model.classifier[1] = nn.Linear(butterfly_model.classifier[1].in_features, len(self.butterfly_species))

            # Load the saved state dictionary for the butterfly species model
            butterfly_model.load_state_dict(torch.load('NN/butterfly_model.pth'))

            # Set the butterfly species model to evaluation mode
            butterfly_model.eval()

            # Make a prediction for the butterfly species
            with torch.no_grad():
                species_prediction = butterfly_model(image)
            predicted_species_class = np.argmax(species_prediction[0]).item()
            predicted_species = self.butterfly_species[predicted_species_class]
        
        return predicted_animal, predicted_species
    

if __name__ == '__main__':
    classifier = AnimalClassifier()

    print(classifier.classify('NN/monarch.jpg'))