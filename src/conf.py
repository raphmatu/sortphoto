
import os
from pathlib import Path

dictFormat = {
    'photo': ['.JPG', '.PNG', '.GIF', '.WEBP', '.TIFF', '.PSD', '.RAW', '.BMP', '.HEIF', '.INDD', '.JPEG', '.SVG',
              '.AI', '.EPS', '.PDF'],
    'video': ['.WEBM', '.MPG', '.MP2', '.MPEG', '.MPE', '.MPV', '.OGG', '.MP4', '.M4P', '.M4V', '.AVI', '.WMV',
              '.MOV', '.QT', '.FLV', '.SWF', '.AVCHD']}

fileToIgnore = ['.DS_Store']

FOLDER = os.path.join(str(Path(__file__).parents[1]))