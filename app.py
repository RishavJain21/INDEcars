# Importing required Libraries
from flask import Flask, render_template, request, url_for, make_response, session, redirect
import pandas as pd
import numpy as np
import pickle 

# import pdfkit
# import os
# import platform
# import subprocess

# #setting and configuring path for pdfkit to work
# def _get_pdfkit_config():
#      if platform.system() == 'Windows':
#          return pdfkit.configuration(wkhtmltopdf=os.environ.get('WKHTMLTOPDF_BINARY', 'C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe'))
#      else:
#          WKHTMLTOPDF_CMD = subprocess.Popen(['which', os.environ.get('WKHTMLTOPDF_BINARY', 'wkhtmltopdf')], stdout=subprocess.PIPE).communicate()[0].strip()
#          return pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_CMD)

app = Flask(__name__)
app.config['SECRET_KEY']='super_secret_key'
 
@app.route("/")
def default():
    return render_template('index.html')

@app.route("/index")
def index():
    return render_template('index.html')

@app.route("/getstart")
def getstart():
    return render_template('getstart.html')

@app.route("/features")
def features():
    #reading the dataset
    path='data_analysis/dataset/no_null_df.csv'
    df = pd.read_csv(path)

    #dropping irrelevant features
    df.drop(['Model', 'Variant', 'Front_Suspension', 'Rear_Suspension', 'Front_Tyre_&_Rim', 'Rear_Tyre_&_Rim', 'Power', 'Torque', 'Wheels_Size'],axis=1,inplace=True)

    # dividing into object float and bool columns
    object_columns=df.select_dtypes(include=['object']).columns
    float_columns=df.select_dtypes(include=['float64']).columns
    bool_columns=df.select_dtypes(include=['bool']).columns
    
    #making list of boolean columns
    b_dict=list(bool_columns)

    #making dictionary of object variables as key and their unique values as result
    o_dict={}
    for c in object_columns:
        l=list(df[c].unique())
        l.sort()
        o_dict[c]=l

    #making dictionary of float variables as key and their min, max and mean values as result
    df1=df[float_columns].describe()
    df2=df1.transpose()
    df3=df2[['min','max','mean']]
    df3=df3.round(0)
    df3=df3.transpose()
    
    return render_template('features.html', f_dict=df3,b_dict=b_dict, o_dict=o_dict)

@app.route("/visualize", methods=['GET','POST'])
def visualize():
    filtered=0
    selected_graph=pd.DataFrame()

    #reading the dataset and dropping unnnamed column
    graph_df=pd.read_csv('data_analysis/dataset/data_vis.csv')
    graph_df.drop('Unnamed: 0',axis=1)

    #finding different variables and types available
    vars_l=graph_df.variable_1.unique()
    vars_l=list(vars_l)
    vars_l=sorted(vars_l)
    types_l=graph_df.Type.unique()
    types_l=list(types_l)
    types_l=sorted(types_l)

    graph_df["variable_2"].fillna("None", inplace = True)

    if request.method == 'POST':
        # determining which form was submitted and slecting graph accordingly
        if 'Type' in request.form:
            #when type form is submitted
            type=str(request.form['Type'])
            selected_graph=graph_df[graph_df['Type']==type]
        else:
            #when variable form is submitted
            if(request.form.getlist('Variable_1')!=[''] and request.form.getlist('Variable_2')!=['']):
                #when both variables are entered
                var1=str(request.form['Variable_1'])
                var2=str(request.form['Variable_2'])
                if(var1==var2):
                    #when both entered variables are entered are same
                    selected_graph=graph_df[graph_df['variable_1']==var1]
                else:
                    selected_graph=graph_df[graph_df['variable_1']==var1]
                    selected_graph=selected_graph[graph_df['variable_2']==var2]
                filtered=1
            elif(request.form.getlist('Variable_1')!=['']):
                #when both variable_1 is entered
                var1=str(request.form['Variable_1'])
                selected_graph=graph_df[graph_df['variable_1']==var1]
                filtered=1
            elif(request.form.getlist('Variable_2')!=['']):
                #when both variable_2 is entered
                var2=str(request.form['Variable_2'])
                selected_graph=graph_df[graph_df['variable_1']==var2]
                selected_graph = pd.concat([selected_graph,graph_df[graph_df['variable_2']==var2]])
                filtered=1
            else:
                #when empty form is submitted
                filtered=0
    return render_template('visulaize.html',vars_l=vars_l,types_l=types_l,filtered=filtered,graphs=selected_graph.to_dict('records'))

@app.route("/recommend", methods=['GET','POST'])
def recommend():
    #reading the dataset
    path='data_analysis/dataset/no_null_df.csv'
    df = pd.read_csv(path)
    
    #relevent columns
    object_columns=df[['Make','Drivetrain','Emission_Norm','Fuel_Type','Body_Type','Gears','Front_Brakes','Rear_Brakes','Power_Steering','Power_Windows','Keyless_Entry','Type','Third_Row_AC_Vents','Ventilation_System','Parking_Assistance']]
    bool_columns=df[['Central_Locking','Auto-Dimming_Rear-View_Mirror','Navigation_System','Second_Row_AC_Vents','Rain_Sensing_Wipers']]
    float_columns=df[['Ex-Showroom_Price(Rs)','Cylinders','Height(mm)','Length(mm)','Width(mm)','City_Mileage(km/litre)','Ground_Clearance(mm)','Seating_Capacity','Wheelbase','Minimum_Turning_Radius(meter)','Number_of_Airbags']]
    
    #making list of boolean columns
    b_dict=list(bool_columns)

    #making dictionary of object variables as key and their unique values as result
    o_dict={}
    for c in object_columns:
        l=list(df[c].unique())
        sorted(l)
        o_dict[c]=l

    #making dictionary of float variables as key and their min, max values as result
    df1=df[list(float_columns)].describe()
    df2=df1.transpose()
    df3=df2[['min','max']]
    df3=df3.transpose()
    if request.method == 'POST':
        new_data_point=[]
        X=[]

        #adding entered feilds and values to X and new_data_point respectively
        for c in float_columns:
            if(request.form.getlist(c)!=['']):
                new_data_point.append(float(request.form[c]))
                X.append(c)
        for c in bool_columns:
            if(request.form.getlist(c)!=[]):
                new_data_point.append(bool(request.form.getlist(c)))
                X.append(c)
        for c in object_columns:
            if(request.form.getlist(c)!=['']):
                new_data_point.append(str(request.form[c]))
                X.append(c)
        choices = {X[i]: new_data_point[i] for i in range(len(X))}
        session['choices']=choices
        Xcol=X
        X=df[X]
        if(new_data_point==[]):
            warning="Please enter some preferances!"
            return render_template('recommend.html',f_dict=df3,b_dict=b_dict, o_dict=o_dict,warning=warning)
        for index,c in enumerate(Xcol):
            # one hot encoding object values
            if(X[c].dtype==object):
                X.loc[df[c] == new_data_point[index], c] = 1
                X.loc[df[c] != new_data_point[index], c] = 0
                new_data_point[index]=1
            # bool values to number
            if(X[c].dtype==bool):
                X.loc[df[c] == True, c] = 1
                X.loc[df[c] != False, c] = 0
                new_data_point[index]=1

        #converting entered values and X to float
        new_data_point = [float(i) for i in new_data_point]
        X = X.astype(float)

        #normalization
        for index,c in enumerate(Xcol):
            mean=X[c].mean()
            std=X[c].std()
            X[c]=(X[c]-mean)/std
            new_data_point[index]=(new_data_point[index]-mean)/std

        #finding k nearest neighbours
        distances = np.linalg.norm(X - new_data_point, axis=1)
        k = 5 
        nearest_neighbor_ids = distances.argsort()[:k]

        # finding and storing data of k nearest neighbours from original dataset
        data=pd.read_csv('data_analysis/dataset/cars_engage_2022.csv')
        lst=[]
        for i in nearest_neighbor_ids:
            mod=data.iloc[i]
            mod.dropna(axis=0, inplace=True)
            lst.append(mod.to_dict())
        session['recs']=lst 
        session['no_of_recs']=k
        return redirect("/recommended_result")

    return render_template('recommend.html',f_dict=df3,b_dict=b_dict, o_dict=o_dict, warning="")

@app.route("/recommended_result")
def recommended_result():
    recs=session['recs']
    no_of_recs=session['no_of_recs']
    return render_template('recommended_result.html',recs=recs,count=list(range(0,no_of_recs)))

# @app.route("/recommended_result_pdf/<index>")
# def recommended_result_pdf(index):
#     recs=session['recs']
#     index=int(index)
#     if(index!=-1):
#         # particular recommendation is downloaded
#         recs=recs[index]
#         recs=[recs]
#     choices=session['choices']

    # #rendering html as pdf
    # rendered = render_template('recommendation_pdf.html',recs=recs,choices=choices)
    # pdf = pdfkit.from_string(rendered,False,configuration=_get_pdfkit_config())
    # response = make_response(pdf)
    # response.headers['Content-Type']='application/pdf'
    # response.headers['Content-Disposition']='attachment;filename-recommendation.pdf'
    # return response

@app.route("/predict", methods=['GET','POST'])
def predict():

    #reading the dataset
    path='data_analysis/dataset/no_null_df.csv'
    df = pd.read_csv(path)

    #relevant columns decided by exploratory data analysis(in eda notebook)
    float_cols=['Displacement(cc)','Cylinders','Fuel_Tank_Capacity(litres)','Wheelbase','Highway_Mileage(km/litre)'
        ,'Seating_Capacity','Number_of_Airbags']
    bool_cols=['Hill_Assist','ESP_(Electronic_Stability_Program)',
        'Rain_Sensing_Wipers','Leather_Wrapped_Steering','Automatic_Headlamps','ASR_Traction_Control'
        ,'Cruise_Control']
    df = df[float_cols+bool_cols]
    df=df.describe()
    df=df.transpose()
    df=df[['mean','std']]
    df['low']=round(df['mean']-df['std'],0)
    df['high']=round(df['mean']+df['std'],0)
    # df=df[['low','high']]
    df=df.transpose()
    x=[]
    if request.method == 'POST':
        #access the data from form
        for f in float_cols:
            if(request.form.getlist(f)!=['']):
                x.append(float(request.form[f]))
            else:
                x.append(round(float(df[f]['mean']),0))

        for b in bool_cols:
            x.append(bool(request.form.getlist(b)))

        X=['Displacement','Cylinders','Fuel_Tank_Capacity','Wheelbase','Highway_Mileage','Seating_Capacity','Number_of_Airbags','Hill_Assist','Electronic_Stability_Program','Rain_Sensing_Wipers','Leather_Wrapped_Steering','Automatic_Headlamps','Traction_Control','Cruise_Control']

        # read model
        model = pickle.load(open('data_analysis/price_prediction_model.pkl','rb'))

        # reading non normalized dataframe
        nndf=pd.read_csv('data_analysis/dataset/no_null_df.csv')
        input_cols=x.copy()
        x_float_cols=['Displacement(cc)','Cylinders','Fuel_Tank_Capacity(litres)','Wheelbase','Highway_Mileage(km/litre)','Seating_Capacity','Number_of_Airbags']

        #normalize input
        def normalize(input):
            for index,c in enumerate(x_float_cols):
                input[index]=(input[index]-nndf[c].min())/(nndf[c].max()-nndf[c].min())
            return input 
        normalized_input=normalize(input_cols)

        #getting prediction
        prediction = model.predict([normalized_input])
        output = round(prediction[0], 2) 

        #setting warning message
        warning=""
        if(output<0):
            warning="The prediction is negative, the input values are beyond the scope of prediction for this model. Please try again."

        spec = {X[i]: x[i] for i in range(len(X))}
        return render_template("predict_result.html", prediction_text='Your predicted price of car for specified features is Rs {}'.format(output),spec=spec,warning=warning)
    return render_template('predict.html',ranges=df,f_list=float_cols,b_list=bool_cols)

if __name__ == "__main__":
    app.run(debug=True)


