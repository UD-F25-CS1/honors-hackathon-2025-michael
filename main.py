from bakery import assert_equal
from drafter import *
from dataclasses import dataclass

hide_debug_information()
set_website_framed(False)
set_website_title("Nutrition Budgeting Game")
set_site_information(
    "Michael Guarino",
    """
This website is an educational game in which the player receives a randomly generated
amount of money and has to use that money to feed their player for 30 days. This game
is designed to teach players how to eat a nutritious diet while also teaching them
how to budget. 
""",
    [],
    [],
    [],
)

prices = {"Sugar/Candy": 1,
          "Carbs": 3,
          "Vegetable": 5,
          "Fruit": 8,
          "Dairy": 7,
          "Meat": 10}
'''Prices are loosely based on cost per portion according to:
https://ers.usda.gov/sites/default/files/_laserfiche/publications/44678/19980_eib96.pdf'''

recipes = {"Salad": [0,0,3,0,0,0],
           "Meat Stew": [0,1,3,0,0,2],
           "Cheeseburger": [0,1,0,0,1,2],
           "Baked Fish with Rice": [0,1,1,0,0,1],
           "Yogurt Bowl": [0,0,0,1,1,0],
           "Vegetable Stew": [0,1,4,0,0,0],
           "Tacos": [0,1,2,0,1,1],
           "Cake": [1,1,0,0,1,0],
           "Fruit Smoothie": [1,0,0,3,1,0],
           "Candy": [1,0,0,0,0,0],}

recipe_value = {"Salad": 3,
                "Meat Stew": 5,
                "Cheeseburger": 2,
                "Baked Fish with Rice": 6,
                "Yogurt Bowl": 3,
                "Vegetable Stew": 4,
                "Tacos": 3,
                "Cake": 1,
                "Fruit Smoothie": 2,
                "Candy": 1,}

@dataclass
class State:
    budget: int
    day: int
    hunger: int #If hunger reaches 0, the player loses the game
    refrigerator: dict[str, int]
    unhealthy: int
    fridge_time: dict[str, list[int]]
    returned_unhealthy: bool
    returned_overeat: bool

@route
def index(state: State) -> Page:
    '''This route returns the "Home Page" of the website and resets values of state fields.
    Arguments:
        state (State): current state of the website
    Returns:
        Page: The returned page will allow the player to view the rules or begin the game.
    '''
    state.budget = 300
    state.day = 1
    state.hunger = 8
    state.refrigerator = {"Sugar/Candy": 0,
                          "Carbs": 0,
                          "Vegetable": 0,
                          "Fruit": 0,
                          "Dairy": 0,
                          "Meat": 0}
    state.fridge_time = {"Sugar/Candy": [],
                         "Carbs": [],
                         "Vegetable": [],
                         "Fruit": [],
                         "Dairy": [],
                         "Meat": []}
    state.returned_unhealthy = False
    state.returned_overeat = False
    return Page(state,
                [Header("Nutrition Budgeting Game", 1),
                 "Welcome to the Nutrition Budgeting Game!",
                 "Please view the rules by clicking the button below",
                 Button("How To Play", "view_instructions"),
                 "To begin the game, please click the button below",
                 Button("Begin Game", "play_game")])

@route
def view_instructions(state: State) -> Page:
    content = [Header("Game Instructions", 1),
               '''Welcome to the Nutrition Budgeting Game where your goal is to use your allotted
budget to feed your player over the course of 30 days''', 
''' - When you begin the game, you will receive a randomly generated amount of money as your budget
 for the 30 days.''', 
''' - Your player statistics, including hunger level, will be listed at the top of the website.
 If your hunger level reaches 0, you will lose the game. Hunger progresses each day.''', 
''' - Your player must also make sure to eat a healthy diet. Eating an unhealthy diet will incur score
 penalties and in-game penalties, like sickness.''', 
" - You will be able to progress through each day by clicking the 'Proceed' button.", 
" - To purchase foods, you must visit the store.", 
''' - When you purchase foods, they go into your refrigerator. Items in your refrigerator will go bad
 after 7 days and need to be thrown out.''', 
" - Your refrigerator also can only hold up to 15 items at a time.", 
''' - Using the food items in your refrigerator, you can create meals for your player. Meals will
 provide varying amounts of hunger to your player depending on how healthy they are.''', 
" - Be on the lookout for feedback from the website about your diet to avoid penalties.", 
"Good luck and have fun!",
Button("Return to Home", "index")]
    return Page(state, content)
                 
@route
def play_game(state: State) -> Page:
    if state.hunger <= 0 or state.unhealthy >= 8 or state.hunger >= 15:
        return lose_game(state)
    if state.day == 30:
        return win_game(state)
    if state.unhealthy >= 5 and not state.returned_unhealthy:
        state.returned_unhealthy = True
        return Page(state,
                    [f'''Warning: You have eaten {state.unhealthy} unhealthy foods. If you eat 8
total unhealthy foods, you will lose the game.''',
                     Button("Return to Main Screen", "play_game")])
    if state.hunger > 10 and not state.returned_overeat:
        state.returned_overeat = True
        return Page(state, [f'''Warning: You have eaten too much food. If your hunger bar reaches
15, you will lose the game.''',
                     Button("Return to Main Screen", "play_game")])
    hunger_bar = state.hunger * "🍗"
    content = [float_right(Button("Quit", "index")),
               Header("Player Statistics", 3),
               Table([[f"Budget: {state.budget}"], [f"Day: {state.day}"], [f"Hunger Bar: {hunger_bar}"]]),
               Header("Actions:", 3),
               Row(Button("Visit Shop", "visit_shop"),
                   Button("View Refrigerator", "view_refrigerator"),
                   Button("Proceed", "advance_day"))]
    return Page(state, content)

@route
def visit_shop(state: State) -> Page:
    shop_grid = [[Header("Item:", 4)],[Header("Price:", 4)],[""]]
    for key, value in prices.items():
        shop_grid[0].append(Header(key, 4))
        shop_grid[1].append(Header(str(value), 4))
        shop_grid[2].append(Button("Purchase", "purchase_food", Argument("item", key)))
    content = [float_right(Button("Quit", "index")),
               Header("Welcome to the Shop!", 2),
               f"Current Balance: {state.budget}",
               Table(shop_grid),
               Row(Button("Return to Main Screen", "play_game"),
                   Button("View Refrigerator", "view_refrigerator"))]
    return Page(state, content)

@route
def purchase_food(state: State, item: str) -> Page:
    price = prices[item]
    num_items = 0
    for value in state.refrigerator.values():
        num_items += value
    if num_items >= 15:
        return Page(state, [float_right(Button("Quit", "index")),
                            "Error: You do not have enough space in your refrigerator to purchase this item",
                            Button("Return to Shop", "visit_shop")])
    if state.budget > price:
        state.budget -= price
        state.refrigerator[item] += 1
        state.fridge_time[item].append(0)
    else:
        return Page(state, [float_right(Button("Quit", "index")),
                            "Error: You do not have enough money to purchase this item",
                            Button("Return to Shop", "visit_shop")])
    return visit_shop(state)

@route
def advance_day(state: State) -> Page:
    state.day += 1
    state.hunger -= 4
    for food in state.fridge_time:
        for list_index in range(0,len(state.fridge_time[food])):
            state.fridge_time[food][list_index] += 1
            if state.fridge_time[food][list_index] == 6:
                return Page("Warning: One of your food items is a day away from expiring",
                            Button("Return to Main Screen", "play_game"))
            if state.fridge_time[food][list_index] > 6:
                state.refrigerator[food] -= 1
                state.fridge_time[food][list_index], state.fridge_time[food][-1] = [state.fridge_time[food][-1],
                                                                                    state.fridge_time[food][list_index]]
                state.fridge_time[food].pop()
                return Page("Warning: One of your food items expired and was thrown away",
                            Button("Return to Main Screen", "play_game"))
    return play_game(state)

@route
def view_refrigerator(state: State) -> Page:
    if state.hunger == 0 or state.unhealthy >= 8 or state.hunger >= 15:
        return lose_game(state)
    if state.day == 30:
        return win_game(state)
    if state.unhealthy >= 5 and not state.returned_unhealthy:
        state.returned_unhealthy = True
        return Page(state,
                    [f'''Warning: You have eaten {state.unhealthy} unhealthy foods. If you eat 8
total unhealthy foods, you will lose the game.''',
                     Button("Return to Main Screen", "play_game")])
    if state.hunger > 10 and not state.returned_overeat:
        state.returned_overeat = True
        return Page(state, [f'''Warning: You have eaten too much food. If your hunger bar reaches
15, you will lose the game.''',
                     Button("Return to Main Screen", "play_game")])
    fridge_grid = [[Header("Item:", 4)],
                   [Header("Quantity:", 4)],
                   [Header("Days before spoiling:", 4)]]
    for food, value in state.refrigerator.items():
        fridge_grid[0].append(Header(food, 4))
        fridge_grid[1].append(Header(str(value), 4))
        spoiling_time = ""
        for list_index, time in enumerate(state.fridge_time[food]):
            spoiling_time += str(7-time)
            if list_index < len(state.fridge_time[food])-1:
                spoiling_time += ", "
        fridge_grid[2].append(Header(spoiling_time, 4))
    hunger_bar = state.hunger * "🍗"
    return Page(state, [float_right(Button("Quit", "index")),
                        Header("Refrigerator", 2),
                        Row("Hunger: " + hunger_bar),
                        Table(fridge_grid),
                        Row(Button("Return to Main Screen", "play_game"),
                            Button("Visit Shop", "visit_shop"),
                            Button("Feed Player", "make_recipe"))])

@route
def make_recipe(state: State) -> Page:
    recipe_grid =[[Header("Recipe:", 4)],
                  [Header("Sugar/Candy Required:", 4)],
                  [Header("Carbs Required:", 4)],
                  [Header("Vegetables Required:", 4)],
                  [Header("Fruits Required:", 4)],
                  [Header("Dairy Required:", 4)],
                  [Header("Meat Required:", 4)],
                  [" "]]
    for key, value in recipes.items():
        recipe_grid[0].append(Header(key, 4))
        for num in range(1,7):
            recipe_grid[num].append(Header(str(value[num-1]), 4))
        recipe_grid[7].append(Button("Feed Player", "feed_player", Argument("item", key)))
    hunger_bar = state.hunger * "🍗"
    return Page(state, [float_right(Button("Quit", "index")),
                        Header("Recipes:", 2),
                        Row("Hunger: " + hunger_bar),
                        f"Current Balance: {state.budget}",
                        Table(recipe_grid),
                        Row(Button("Return to Main Screen", "play_game"),
                            Button("Visit Shop", "visit_shop"),
                            Button("View Refrigerator", "view_refrigerator"))])

@route
def feed_player(state: State, item: str) -> Page:
    if item == "Cake" or item == "Candy":
        state.unhealthy += 1
    food_used = recipes[item]
    food_items = []
    for key in prices:
        food_items.append(key)
    for list_index, quantity in enumerate(food_used):
        food = food_items[list_index]
        if state.refrigerator[food] >= quantity:
            state.refrigerator[food] -= quantity
            for num in range(0, quantity):
                state.fridge_time[food][0], state.fridge_time[food][-1] = [state.fridge_time[food][-1],
                                                                           state.fridge_time[food][0]]
                state.fridge_time[food].pop()
        else:
            return Page(state, ["Error: You do not have enough of the required food items for this recipe",
                                Row(Button("Return to Main Screen", "play_game"),
                                Button("Visit Shop", "visit_shop"),
                                Button("View Refrigerator", "view_refrigerator"))])
    state.hunger += recipe_value[item]
    return view_refrigerator(state)

@route
def lose_game(state: State) -> Page:
    '''This route is called when the player's hunger reaches 0 or the player eats
    8 unhealthy foods
    Arguments:
        state (State): current state of the website
    Returns:
        Page: defeat page of the website, with a button linking back to the index route
    '''
    return Page(state, [f"You lost after {state.day} days!",
                        Button("Return to Home", "index")])

@route
def win_game(state: State) -> Page:
    '''This route is called when the player makes it through all 30 simulated days.
    Arguments:
        state (State): current state of the website
    Returns:
        Page: victory page of the website, with a button linking back to the index route
    '''
    return Page(state, [f"You won with {state.budget} remaining!",
                        Button("Return to Home", "index")])

set_website_style("tacit")
start_server(State(0,0,8,{},0,{}, False, False))
