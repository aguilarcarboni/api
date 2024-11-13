import pandas as pd

class Architecture:
    def __init__(self):
        self.grade_data = {
            'Homework': [100, 75, 95, 90, 90, 45, 90],
            'Quizzes': [100, 60, 80, 90, 90, 80, 80, 50, 100],
            'Project': 75,
        }

        self.weights = {
            'Homework': 0.4,
            'Quizzes': 0.4,
            'Project': 0.2
        }

class SoftwareEngineering:
    def __init__(self):
        self.grade_data = {
            'Project': 100,
            'Midterm 1': 74, 
            'Midterm 2': 84,
        }

        self.weights = {
            'Project': 0.5,
            'Midterm 1': 0.25,
            'Midterm 2': 0.25
        }

class ObjectOriented:
    def __init__(self):
        self.grade_data = {
            'Homework': [100, 100, 100],
            'Quizzes': [90, 90, 100],
            'Project 1': 84,
            'Project 2': 100,
            'Final Project': 85, 
        }

        self.weights = {
            'Homework': 0.1,
            'Quizzes': 0.1,
            'Project 1': 0.25,
            'Project 2': 0.25,
            'Final Project': 0.3
        }

class Algorithms:
    def __init__(self):
        self.grade_data = {
            'Quizzes': [100, 0, 0, 0, 0, 0, 20, 85, 0, 90, 0, 50, 70, 90, 70, 100, 75, 100, 100, 0],
            'Participation': 100,
            'Project 1': 96,
            'Midterm': 84,
            'Project 2': 95,
            'Final Exam': 80
        }

        self.weights = {
            'Quizzes': 0.2,
            'Participation': 0.05,
            'Project 1': 0.1,
            'Midterm': 0.15,
            'Project 2': 0.25,
            'Final Exam': 0.25
        }

class GradeCalculator:

    def __init__(self, algorithms: Algorithms):

        self.grade_data = algorithms.grade_data
        self.weights = algorithms.weights
        self.grades_df = pd.DataFrame(columns=['Unweighted Grade', 'Weight', 'Weighted Grade'])

    def calculate_grades(self):
        for assignment, grade in self.grade_data.items():
            unweighted = sum(grade) / len(grade) if isinstance(grade, list) else grade
            weight = self.weights[assignment]
            weighted = unweighted * weight
            
            self.grades_df.loc[assignment] = [unweighted, weight, weighted]

    def print_grades(self):
        print("\nGrade Summary:")
        print(self.grades_df)
        print(f"Final Grade: {self.grades_df['Weighted Grade'].sum():.2f}")

if __name__ == "__main__":
    
    print("Algorithms")
    algorithms = Algorithms()
    calculator = GradeCalculator(algorithms)
    calculator.calculate_grades()
    calculator.print_grades()

    print("\nObject Oriented")
    object_oriented = ObjectOriented()

    calculator = GradeCalculator(object_oriented)
    calculator.calculate_grades()
    calculator.print_grades()

    print("\nArchitecture")
    architecture = Architecture()
    calculator = GradeCalculator(architecture)
    calculator.calculate_grades()
    calculator.print_grades()

    print("\nSoftware Engineering")
    software_engineering = SoftwareEngineering()
    calculator = GradeCalculator(software_engineering)
    calculator.calculate_grades()
    calculator.print_grades()
