from bakery import assert_equal
from drafter import *
from dataclasses import dataclass

# hide_debug_information()
# set_website_framed(False)
set_website_title("Nutrition Budgeting Game")
set_site_information(
    "Michael Guarino",
    """
This website is an educational game in which the player receives a randomly generated
amount of money and has to use that money to feed their player for 30 days. 
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

@dataclass
class State:
    budget: int
    day: int
    hunger: int #If hunger reaches 0, the player loses the game
    refrigerator: dict[str, int]

@route
def index(state: State) -> Page:
    state.budget = 400
    state.day = 1
    state.hunger = 6
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
    if state.hunger == 0:
        return lose_game(state)
    if state.day == 30:
        return win_game(state)
    hunger_bar = state.hunger
    content = [float_right(Button("Quit", "index")),
               Header("Player Statistics", 3),
               Table([[f"Budget: {state.budget}"], [f"Day: {state.day}"], [f"Hunger: {hunger_bar}"]]),
               Header("Actions:", 3),
               Row(Button("Visit Store", "visit_store"), Button("Proceed", "advance_day"),
                   Button("View Refrigerator", "view_refrigerator"))]
    return Page(state, content)

@route
def visit_store(state: State) -> Page:
    shop_grid = [[Header("Item:", 4) ],[Header("Price:", 4)],[""]]
    for key, value in prices.items():
        shop_grid[0].append(Header(key, 4))
        shop_grid[1].append(Header(str(value), 4))
        shop_grid[2].append(Button("Purchase", "purchase_food"))
    content = [Header("Welcome to the Store", 2),
               Table(shop_grid)]
    return Page(state, content)

@route
def purchase_food(state: State) -> Page:
    pass

@route
def advance_day(state: State) -> Page:
    state.day += 1
    state.hunger -= 2
    return play_game(state)

@route
def view_refrigerator(state: State) -> Page:
    pass

@route
def lose_game(state: State) -> Page:
    return Page(state, [f"You lost after {state.day} days!",
                        Button("Return to Home", "index")])

@route
def win_game(state: State) -> Page:
    return Page(state, [f"You won with {state.budget} remaining!",
                        Button("Return to Home", "index")])

set_website_style("tacit")
start_server(State(0,0,6,{}))
