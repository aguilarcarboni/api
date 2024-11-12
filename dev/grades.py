import pandas as pd

class Algorithms:
    def __init__(self):
        self.grade_data = {
            'Quizzes': [
                100,
                0,
                0,
                0,
                0,
                0,
                20,
                85,
                0,
                90,
                0,
                50,
                70,
                90,
                70,
                100,
                75,
                100,
                0,
                0
            ],
            'Participation': 100,
            'Project 1': 96,
            'Project 2': 90,
            'Midterm': 84,
            'Final Exam': 90
        }

        self.weights = {
            'Quizzes': 0.2,
            'Participation': 0.05,
            'Project 1': 0.1,
            'Project 2': 0.25,
            'Midterm': 0.15,
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
    
    algorithms = Algorithms()
    calculator = GradeCalculator(algorithms)

    calculator.calculate_grades()
    calculator.print_grades()