class RecipeBuilder:
    def __init__(self):
        pass

    @staticmethod
    def reformate_ingredients(ingredients: str) -> list:
        return ingredients.strip().split(",")


builder = RecipeBuilder()
