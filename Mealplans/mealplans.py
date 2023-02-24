import numpy as np
import pandas as pd
import requests
import json
import time
import ast
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from IPython.display import display
from pyairtable import Api, Base, Table
from PIL import Image
from wordcloud import WordCloud, STOPWORDS
from io import BytesIO


class client:
    
    def __init__(self,name,surname,kcal,menudays,diet, exclude, address, client_id):
            
        #Name es la variable que recogerá el nombre aleatorio de cada instancia de cliente

        self.name = name

        #Surname es la variable que recogerá el apellido aleatorio de cada instancia de cliente

        self.surname = surname

        #Kcal es la variable que recogerá las kcal aleatorias para crear el menú de cada instancia de cliente

        self.kcal = kcal

        #Menudays es la variable que recogerá para qué días aleatorios quiere recibir menú de cada instancia de cliente

        self.menudays = menudays
        
        #Diet es la variable que recogerá una dieta aleatoria de cada instancia de cliente

        self.diet = diet

        #Exclude es la variable que recogerá qué alimentos aleatorios se quieren excluir del menú de cada instancia de cliente

        self.exclude = exclude

        #Address es la variable que recogerá la dirección aleatoria de cada instancia de cliente

        self.address = address
        
        #client_id es la variable que recogerá el id del cliente para poder añadirlo a Airtable, y filtrar en base a él para extraer los datos

        self.client_id = client_id
        
##### Funciones para mostrar y editar la información inicial #########################################################################
    
    def display_info(self):
        
        print(f"Name: {self.name}")
        print(f"Surname: {self.surname}")
        print(f"Calories: {self.kcal}")        
        print(f"Days of the menu: {self.menudays}")
        print(f"Kind of diet: {self.diet}")
        print(f"Excluded ingredients: {self.exclude}")
        print(f"Address: {self.address}")
        
        return [self.name, self.surname, self.kcal, self.menudays, self.diet, self.exclude, self.address, self.client_id]
        
    
    def edit_name(self, new_name):
        
        self.last_name = self.name
        self.name = new_name
        
        print(f"You changed from: {self.last_name} to {self.name}")
        
    def edit_surname(self, new_surname):
        
        self.last_surname = self.surname
        self.surname = new_surname
        
        print(f"You changed from: {self.last_surname} to {self.surname}")

    def edit_kcal(self, new_kcal):

        self.last_kcal = self.kcal
        self.kcal = new_kcal
        
        print(f"You changed from: {self.last_kcal} to {self.kcal}")
        
    def edit_menudays(self, new_menudays):
        
        self.last_menudays = self.menudays        
        self.menudays = new_menudays
        
        print(f"You changed from: {self.last_menudays} to {self.menudays}")
        
    def edit_diet(self, new_diet):
        
        self.last_diet = self.diet        
        self.diet = new_diet
        
        print(f"You changed from: {self.last_diet} to {self.diet}")
        
    def edit_exclude(self, new_exclude):
        
        self.last_exclude = self.exclude        
        self.exclude = new_exclude
        
        print(f"You changed from: {self.last_exclude} to {self.exclude}")
        
    def edit_address(self, new_address):
        
        self.last_address = self.address
        self.address = new_address
        
        print(f"You changed from: {self.last_address} to {self.address}")
        
######################################################################################################################################


##### Funciones para crear menú individualizado #########################################################################
    
    def create_calendar_menu(self):
            
        url = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/mealplans/generate"

        querystring = {"timeFrame":"week","targetCalories":self.kcal, "diet": self.diet,"exclude":self.exclude}

        headers = {
            "X-RapidAPI-Key": "59cc29ff14msh658ecb9cb09c72ep188b74jsn70e58d04961d",
            "X-RapidAPI-Host": "spoonacular-recipe-food-nutrition-v1.p.rapidapi.com"
        }
        
        self.list_ids, self.list_menu_ids, self.list_recipes, self.list_daily_recipes = [],[],[],[]

        while len(self.list_ids) < (len(self.menudays)*3):
            
            response = requests.request("GET", url, headers=headers, params=querystring)
                        
            if len(response.json()["items"]) == 0:
                
                self.list_ids = ["","","","","","","","","","","","","","","","","","","","","","",]
                return "It's not possible to create a calendar menu with this requisites"
            
            for enum, i in enumerate(response.json()["items"]):

                dict_recipe = json.loads(response.json()["items"][enum]["value"])

                self.list_ids.append(dict_recipe["id"])
                self.list_recipes.append(dict_recipe["title"])

        self.menu_calendar = pd.DataFrame()

        for i in range(len(self.menudays)):

            self.list_daily_recipes.append(self.list_recipes[i*3:(i*3)+3])

        for i in range((len(self.menudays)*3)):

            self.list_menu_ids.append(self.list_ids[i])

        for enum, day in enumerate(self.menudays):

            self.menu_calendar[day] = self.list_daily_recipes[enum]

        self.menu_calendar.index = ["Breakfast", "Lunch", "Dinner"]

        return "Calendar menu created!"
    
    def return_calendar_menu(self):
        
        return self.menu_calendar
    
    def display_calendar_menu(self):

        display(self.menu_calendar)
    
    def return_recipes_ids(self):
        
        return self.list_ids
    
######################################################################################################################################    

##### Funciones para lista de la compra individualizada ##############################################################################

    def create_shopping_list(self):
        
        self.list_recipe_info = []

        for id_ in self.list_menu_ids:

            url = f"https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/{id_}/information"

            headers = {
                "X-RapidAPI-Key": "59cc29ff14msh658ecb9cb09c72ep188b74jsn70e58d04961d",
                "X-RapidAPI-Host": "spoonacular-recipe-food-nutrition-v1.p.rapidapi.com"
            }

            querystring = {"includeNutrition":"true"}

            response = requests.request("GET", url, headers=headers, params = querystring)
            self.list_recipe_info.append(response.json())
            time.sleep(1)
    
    
        self.list_ingredient_names, self.list_ingredient_amounts, self.list_ingredient_units = [],[],[]
        self.list_nutrient_names, self.list_nutrient_amounts, self.list_nutrient_units, self.list_nutrient_pdn = [],[],[],[]
        self.list_properties_names, self.list_properties_amounts, self.list_properties_units = [],[],[]


        for recipe in self.list_recipe_info:

            for ingredients in recipe["extendedIngredients"]:

                self.list_ingredient_names.append(ingredients["name"])
                self.list_ingredient_amounts.append(ingredients["amount"])
                self.list_ingredient_units.append(ingredients["unit"])
                
        self.shopping_list = pd.DataFrame()

        self.shopping_list["Ingredient"] = self.list_ingredient_names
        self.shopping_list["Amount"] = self.list_ingredient_amounts
        self.shopping_list["Unit"] = self.list_ingredient_units
        
        return "Shopping list created!"
    
    
    def return_shopping_list(self):
        
        return self.shopping_list
    
    def display_shopping_list(self):

        display(self.shopping_list)
    
    def return_recipe_info(self):
        
        return self.list_recipe_info

    
######################################################################################################################################    

##### Funciones para mostrar y retornar la preparación de las recetas del menú ##############################################################################    
    
    def return_recipes_instructions(self):
        
        recipes = {}
        
        for recipe in self.list_recipe_info:
                                    
            recipe_steps = []

            for enum, steps in enumerate(recipe["analyzedInstructions"][0]["steps"]):
                                
                step = steps["step"]
                
                recipe_steps.append(f"Step {enum+1}: {step}")
                
                recipes[recipe["title"]] = recipe_steps
            
        return recipes
    
    def display_recipes_instructions(self):
        
        for recipe in self.list_recipe_info:
        
            print(recipe["title"])
            print("-"*50)
            
            for enum, steps in enumerate(recipe["analyzedInstructions"][0]["steps"]):
                
                step = steps["step"]

                print(f"Step {enum+1}: {step}")
                print("-"*50)

    
######################################################################################################################################    

##### Funciones de listas de nutrición individualizadas ##############################################################################    
    
    def create_nutrition_lists(self):
        
        for recipe in self.list_recipe_info:

            for nutrients in recipe["nutrition"]["nutrients"]:

                self.list_nutrient_names.append(nutrients["name"])
                self.list_nutrient_amounts.append(nutrients["amount"])
                self.list_nutrient_units.append(nutrients["unit"])
                self.list_nutrient_pdn.append(nutrients["percentOfDailyNeeds"])

            for properties in recipe["nutrition"]["properties"]:
                self.list_properties_names.append(properties["name"])
                self.list_properties_amounts.append(properties["amount"])
                self.list_properties_units.append(properties["unit"])
                
        self.nutrients_list = pd.DataFrame()

        self.nutrients_list["Nutrient"] = self.list_nutrient_names
        self.nutrients_list["Amount"] = self.list_nutrient_amounts
        self.nutrients_list["Unit"] = self.list_nutrient_units
        self.nutrients_list["Percentage of Daily Needs"] = self.list_nutrient_pdn
        
        self.properties_list = pd.DataFrame()

        self.properties_list["Propertie"] = self.list_properties_names
        self.properties_list["Amount"] = self.list_properties_amounts
        self.properties_list["Unit"] = self.list_properties_units
        
        return "Nutrition lists created!"
    
    def return_nutrients_list(self):
        
        return self.nutrients_list
    
    def display_nutrients_list(self):

        display(self.nutrients_list)
    
    def return_properties_list(self):
        
        return self.properties_list
    
    def display_properties_list(self):

        display(self.properties_list)

######################################################################################################################################    

##### Airtable functions #############################################################################################################
 

def load_list_of_clients_to_airtable(list_load_clients,api_key, base_id, table_name):
    
    table = Table(api_key = api_key,
                  base_id = base_id,
                  table_name = table_name)

    for i in range(len(list_load_clients)):

        table.create({"Name"                    : list_load_clients[i][0],       #Añade a la tabla de Airtable el nombre del cliente
                      "Surname"                 : list_load_clients[i][1],       #Añade a la tabla de Airtable el apellido del cliente
                      "Calories"                : str(list_load_clients[i][2]),  #Añade a la tabla de Airtable las calorías deseadas del cliente
                      "Days of the menu"        : str(list_load_clients[i][3]),  #Añade a la tabla de Airtable los días que el cliente quiere recibir menú
                      "Diet"                    : list_load_clients[i][4],       #Añade a la tabla de Airtable la dieta escogida del cliente 
                      "Excluded ingredients"    : list_load_clients[i][5],       #Añade a la tabla de Airtable los ingredientes excluidos del cliente
                      "Address"                 : list_load_clients[i][6],      #Añade a la tabla de Airtable la dirección del cliente
                      "ID"                      : list_load_clients[i][7]})      #Añade a la tabla de Airtable el ID del cliente
    return 

def load_client_to_airtable(load_client,api_key, base_id, table_name):
    
    table = Table(api_key = api_key,
                  base_id = base_id,
                  table_name = table_name)


    table.create({"Name"                    : load_client[0],       #Añade a la tabla de Airtable el nombre del cliente
                  "Surname"                 : load_client[1],       #Añade a la tabla de Airtable el apellido del cliente
                  "Calories"                : str(load_client[2]),  #Añade a la tabla de Airtable las calorías deseadas del cliente
                  "Days of the menu"        : str(load_client[3]),  #Añade a la tabla de Airtable los días que el cliente quiere recibir menú
                  "Diet"                    : load_client[4],       #Añade a la tabla de Airtable la dieta escogida del cliente 
                  "Excluded ingredients"    : load_client[5],       #Añade a la tabla de Airtable los ingredientes excluidos del cliente
                  "Address"                 : load_client[6],       #Añade a la tabla de Airtable la dirección del cliente
                  "ID"                      : load_client[7]})      #Añade a la tabla de Airtable el ID del cliente
    return 
        
def extract_all_clients_from_airtable(api_key, base_id, table_name):
    
    table = Table(api_key = api_key,
                  base_id = base_id,
                  table_name = table_name)

    records = table.all()
    
    airtable_clients = []
    
    for record in records:
        
        airtable_clients.append([record["fields"]["Name"],                 #Añade a la lista el nombre del cliente
                                 record["fields"]["Surname"],              #Añade a la lista el apellido del cliente 
                                 record["fields"]["Calories"],             #Añade a la lista las calorías deseadas del cliente 
                                 record["fields"]["Days of the menu"],     #Añade a la lista los días que el cliente quiere recibir menú
                                 record["fields"]["Diet"],                 #Añade a la lista la dieta escogida del cliente 
                                 record["fields"]["Excluded ingredients"], #Añade a la lista los ingredientes excluidos del cliente 
                                 record["fields"]["Address"],              #Añade a la lista la dirección del cliente  
                                 record["fields"]["ID"]])                  #Añade a la lista el ID del cliente
    return airtable_clients


def extract_client_from_airtable(client_id, api_key, base_id, table_name):
    
    table = Table(api_key = api_key,
                  base_id = base_id,
                  table_name = table_name)

    records = table.all()
    
    for record in records:
        
        if record["fields"]["ID"] == str(client_id):

            client_info = [record["fields"]["Name"],
                          record["fields"]["Surname"],
                          record["fields"]["Calories"],
                          ast.literal_eval(record["fields"]["Days of the menu"]),
                          record["fields"]["Diet"],
                          record["fields"]["Excluded ingredients"],
                          record["fields"]["Address"],
                          record["fields"]["ID"]]

    return client_info

def return_max_id(api_key, base_id, table_name):

    table = Table(api_key = api_key,
                  base_id = base_id,
                  table_name = table_name)

    records = table.all()

    list_records = []

    for record in records:

        list_records.append(int(record["fields"]["ID"]))
        
    max_id = np.max(list_records)
    
    return max_id

    
def delete_all_records(api_key, base_id, table_name):
    
    table = Table(api_key = api_key,
                  base_id = base_id,
                  table_name = table_name)

    records = table.all()
    list_ids = []

    for record in records:

        list_ids.append(record["id"]) 

    table.batch_delete(list_ids)

    return 

######################################################################################################################################    

##### Analyzed plots #############################################################################################################

def return_pie_diets(api_key,base_id,table_name):

    clients = extract_all_clients_from_airtable(api_key, base_id, table_name)

    list_diets=[]

    for diets in clients:

        list_diets.append(diets[4]) #Diets[4] contiene el tipo de dieta de este cliente

    df_diets=pd.DataFrame(list_diets)

    df_diets[0].replace(" ","No diet",inplace=True)

    df_diets = df_diets[0].value_counts()    
    df_diets = df_diets.reset_index()
    df_diets.columns=["Diet","Quantity"]

    fig = plt.figure(figsize = (4, 4))
    fig.set_facecolor('#0E1117')

    plt.pie(x         = df_diets["Quantity"],
            explode   = (0.1, 0.1, 0.1, 0.1),
            labels    = df_diets["Diet"].values,
            shadow    = True,
            autopct   = "%1.1f%%",       
            textprops = {'color':"w"},
            colors    = ["lightgreen", "cyan", "green","orange"])

    return fig

def return_wordcloud_graph(shopping_list):


    text=" ".join(shopping_list["Ingredient"])

    wordcloud_png = np.array(Image.open("corteLogo.png"))
    wordcloud_png.shape


    # Creamos de nuevo el objeto agregando la mascara
    fig = plt.figure(figsize=(5,5))
    fig.set_facecolor('#0E1117')

    wordcloud_obj = WordCloud(background_color = "#0E1117",
                              max_words        = 2000,
                              mask             = wordcloud_png,
                              contour_width    = 2,
                              contour_color    = "white").generate(text)
    
    plt.imshow(wordcloud_obj, interpolation = "bilinear")
    plt.axis("off")

    return fig

def return_sunburst_graph(nutrients_list):

    df_sunburst = nutrients_list

    df_sunburst.groupby(["Nutrient","Unit"]).agg({"Amount":"mean","Percentage of Daily Needs":"mean"})

    df_sunburst = df_sunburst.reset_index()

    fig = px.sunburst(data_frame             = df_sunburst,
                      values                 = "Percentage of Daily Needs",
                      hover_name             = "Amount",
                      color                  = "Percentage of Daily Needs",
                      path                   = ["Nutrient"],
                      color_continuous_scale = 'RdBu')

    return fig

def return_macronutrients_graph(nutrients_list):

    df_bar = nutrients_list

    df_bar = df_bar.groupby(["Nutrient","Unit"]).agg({"Amount":"mean","Percentage of Daily Needs":"mean"})

    df_bar = df_bar.reset_index()

    df_bar_macro = df_bar.loc[df_bar["Nutrient"].isin(("Fat","Carbohydrates","Net Carbohydrates","Sugar","Protein"))]

    df_bar_macro.columns = ["Nutrient","Nutrients","Amount","Percentage of Daily Needs"]

    df_bar_macro["Nutrients"] = ""


    fig = plt.figure(figsize = (10,10))
    
    sns.barplot(x = "Percentage of Daily Needs", y = "Nutrients", hue = "Nutrient", data = df_bar_macro, palette = "rainbow")

    return fig

def return_micronutrients_graph(nutrients_list):

    df_bar = nutrients_list

    df_bar = df_bar.groupby(["Nutrient","Unit"]).agg({"Amount":"mean","Percentage of Daily Needs":"mean"})

    df_bar = df_bar.reset_index()

    df_bar_micro = df_bar.loc[~df_bar["Nutrient"].isin(("Fat","Carbohydrates","Net Carbohydrates","Sugar","Protein"))]

    df_bar_micro.columns=["Nutrient","Nutrients","Amount","Percentage of Daily Needs"]

    df_bar_micro["Nutrients"]=""

    fig = plt.figure(figsize = (10,10))

    sns.barplot(x = "Percentage of Daily Needs", y = "Nutrients", hue = "Nutrient", data = df_bar_micro, palette = "rainbow")


    return fig




######################################################################################################################################    

##### Streamlit #############################################################################################################

st.set_page_config(page_title="Mealplan", page_icon="🥑", layout= "wide")

sb_user_input_pressed = False
api_key = "keyKwTRludsHj7GFw"
base_id = "appM62yZdhosjF9WU"
table_name = "Clients"

tab_user_input, tab_calendar_menu, tab_shopping_list, tab_meal_prep, tab_analysis = st.tabs(["Introduce your menu requisites!",
                                                                                             "My calendar menu",
                                                                                             "My shopping list",
                                                                                             "Steps to cook my meals",
                                                                                             "Graphs about your diet compared!"])
col_text_inputs, col_day_checks, col_diet_rad_buttons = tab_user_input.columns(3)
with tab_user_input:

    with col_text_inputs:

        ti_name                 = st.text_input("Name", "John")
        ti_surname              = st.text_input("Surname", "Davis")
        ti_kcal                 = st.text_input("Calories of your desired menu", "2000")
        ti_excluded_ingredients = st.text_input("Tell us what ingredients you hate!", "raisins, pumpkin")
        ti_address              = st.text_input("Your address (just for sending you the ingredients)", "C. de Campoamor, 13, 28004 Madrid, Spain")

    with col_day_checks:

        st.caption("Choose the days in which you want to receive this menu:")

        check_monday    = st.checkbox("Monday",help="Check this if you want to have menu on Monday")
        check_tuesday   = st.checkbox("Tuesday",help="Check this if you want to have menu on Tuesday")
        check_wednesday = st.checkbox("Wednesday",help="Check this if you want to have menu on Wednesday")
        check_thursday  = st.checkbox("Thursday",help="Check this if you want to have menu on Thursday")
        check_friday    = st.checkbox("Friday",help="Check this if you want to have menu on Friday")
        check_saturday  = st.checkbox("Saturday",help="Check this if you want to have menu on Saturday")
        check_sunday    = st.checkbox("Sunday",help="Check this if you want to have menu on Sunday")

    with col_diet_rad_buttons:

        rb_diet = st.radio("Input your dietary restrictions:",("Vegan","Vegetarian","Paleo","None, just surprise me!"))
    
    sb_user_input = st.button("I'm done! Create my menu!")

    if sb_user_input:
        
        sb_user_input_pressed = True

        list_menudays = []

        if check_monday:

            list_menudays.append("Monday")
        
        if check_tuesday:

            list_menudays.append("Tuesday")
        
        if check_wednesday:

            list_menudays.append("Wednesday")
        
        if check_thursday:

            list_menudays.append("Thursday")
        
        if check_friday:

            list_menudays.append("Friday")
        
        if check_saturday:

            list_menudays.append("Saturday")
        
        if check_sunday:

            list_menudays.append("Sunday")

        if rb_diet == "Vegan":

            client_diet = "vegan"
            
        elif rb_diet == "Vegetarian":

            client_diet = "vegetarian"
            
        elif rb_diet == "Paleo":

            client_diet = "paleo"
            
        elif rb_diet == "None, just surprise me!":

            client_diet = " "

        if ti_excluded_ingredients == "":

            ti_excluded_ingredients = " "

        #Obtenemos el id más alto que ya está en la tabla de Airtable, y le damos el siguiente al nuevo cliente

        newclient_id = str(return_max_id(api_key,base_id,table_name) + 1)
        
        #Creamos un nuevo cliente con toda la información introducida en los formularios
        newclient = [ti_name,ti_surname,ti_kcal,list_menudays,client_diet,ti_excluded_ingredients,ti_address,newclient_id]

        load_client_to_airtable(newclient,api_key,base_id,table_name)

with tab_calendar_menu:

    if sb_user_input_pressed == True:

        myclient_id = str(return_max_id(api_key,base_id,table_name))

        extracted_client = extract_client_from_airtable(myclient_id,api_key,base_id,table_name)

        st.header("This is the calendar menu we have created for you!")
        myclient = client(extracted_client[0],extracted_client[1],extracted_client[2],extracted_client[3],extracted_client[4],extracted_client[5],extracted_client[6],extracted_client[7])
        myclient.create_calendar_menu()
        df_calendar = myclient.return_calendar_menu()
        st.dataframe(df_calendar)


with tab_shopping_list:

    if sb_user_input_pressed == True:

        myclient.create_shopping_list()
        df_shopping_list = myclient.return_shopping_list()

        st.dataframe(df_shopping_list)

with tab_meal_prep:

    if sb_user_input_pressed == True:

        myclient_recipes = myclient.return_recipes_instructions()

        expanders = {recipe : st.expander(recipe) for enum, recipe in enumerate(myclient_recipes.keys())}

        for expander, steps in zip(expanders.values(),myclient_recipes.values()):

            for step in steps:

                expander.write(step)

with tab_analysis:

    m1,m2,m3,m4 = tab_analysis.container(),tab_analysis.container(),tab_analysis.container(),tab_analysis.container()
    l1,r1 = m2.columns(2)
    l2,r2 = m4.columns(2)


    if sb_user_input_pressed == True:
        
        myclient.create_nutrition_lists()

        with m1:

            st.header("These are all the nutrients in your diet!")

            st.subheader("In the following graphs you can see the average PDN of the ingredients in your diet")
            st.subheader("Global, sunburst style")
            st.plotly_chart(return_sunburst_graph(myclient.return_nutrients_list()), theme="streamlit", use_container_width=True)
            
        with l1:

            st.subheader("Micronutrients")
            st.pyplot(return_micronutrients_graph(myclient.return_nutrients_list()))
        
        with r1:

            st.subheader("Macronutrients")
            st.pyplot(return_macronutrients_graph(myclient.return_nutrients_list()))
        
        with m3:
            
            st.header("Some cool graphs now!")

        with l2:

            st.subheader("Main ingredients in your recipes!")
            st.pyplot(return_wordcloud_graph(myclient.return_shopping_list()))

        with r2:

            st.subheader("Our clients most popular diets!")
            st.pyplot(return_pie_diets(api_key,base_id,table_name))








            




    



