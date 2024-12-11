import pandas as pd

# Project 2
# Final Exam
class Algorithms:

    def __init__(self):

        self.grade_data = {
            'Participation': 80,
            'Quizzes': [100, 20, 20, 60, 100, 0, 20, 85, 0, 90, 100, 50, 70, 90, 70, 100, 75, 100, 100, 80],
            'Midterm': 84,
            'Project 1': 96,
            'Project 2': 95,
            'Final Exam': 50
        }

        self.weights = {
            'Participation': 0.05,
            'Quizzes': 0.2,
            'Midterm': 0.15,
            'Project 1': 0.1,
            'Project 2': 0.25,
            'Final Exam': 0.25
        }

# Final Project
# Notes
class ObjectOriented:

    def __init__(self):
        self.grade_data = {
            'Homework': [100, 70, 70],
            'Notes': [100, 100, 0],
            'Quizzes': [90, 90, 100, 45, 85],
            'Project 1': 84,
            'Project 2': 100,
            'Final Project': 95
        }

        self.weights = {
            'Homework': 0.07,
            'Notes': 0.03,
            'Quizzes': 0.1,
            'Project 1': 0.25,
            'Project 2': 0.25,
            'Final Project': 0.3
        }

# Final Project
class Architecture:

    def __init__(self):
        self.grade_data = {
            'Homework': [100, 75, 95, 90, 90, 45, 90, 69, 65, 100],
            'Quizzes': [100, 60, 80, 90, 90, 80, 80, 50, 100, 90, 80, 100],
            'Project': 50
        }

        self.weights = {
            'Homework': 0.4,
            'Quizzes': 0.4,
            'Project': 0.2
        }

# Deliverable 4
class SoftwareEngineering:
    def __init__(self):

        self.grade_data = {
            'Deliverable 1': 98,
            'Deliverable 2': 88,
            'Deliverable 3': 98,
            'Deliverable 4': 120,
            'Midterm 1': 73, 
            'Midterm 2': 63,
        }

        self.weights = {
            'Deliverable 1': 0.1,
            'Deliverable 2': 0.1,
            'Deliverable 3': 0.15,
            'Deliverable 4': 0.15,
            'Midterm 1': 0.25,
            'Midterm 2': 0.25
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
