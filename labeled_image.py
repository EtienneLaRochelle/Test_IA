
import csv


class LabeledImage:
    
    def __init__(self, filename:str, image_dir:str, result_dir:str):
        self.filename = filename
        self.image_dir = image_dir
        self.results_dir = result_dir


    def load_expected_results(self):
        if not self.results_dir:
            self.logger.warning("No results directory specified.")
            return 
        with open(self.results_dir, newline='', encoding='utf-8-sig') as expected_file:
            expected_reader = csv.DictReader(expected_file)
            image_results = []
            for row in expected_reader:
                image_results.append(dict(row))
            return image_results