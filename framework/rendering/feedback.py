class GameplayFeedback:
    @staticmethod
    def trigger_feedback(type):
        if type == "correct":
            print("Visual Flash: Green")
        elif type == "incorrect":
            print("Visual Flash: Red")
