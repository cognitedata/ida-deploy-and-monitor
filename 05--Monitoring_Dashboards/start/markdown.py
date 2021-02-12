markdown_text = '''

### Introduction
Linear regression and random forest regression models are used to 
predict pressure in a wellhead based on historical sensor data. 
The models are trained using a year of timeseries data averaged 
at one minute intervals from four sensors. The models are then used 
to estimate pressure over the next hour of operation for a single sensor. 

### Method
1. Collect timeseries data for four pressure sensors from the 
Open Industrial Dataset using the Cognite Python SDK
2. Initialize the desired model
3. Train the model using three timeseries as inputs, the fourth as output
4. Use the trained model to estimate pressure at a future date
5. Repeat Steps 2 - 4 using additional models
6. Evaluate the statistics of each model (standard error, r2, etc.)

### Implementation
Visit REF for source code.

### Discussion
Both linear regression and random forest regression do a decent job
of predicting pressure as evinced by their respective mean absolute 
errors - which are less than 5%. The r2 score for the random forest
model tends to be higher than that of the linear regression model, 
suggesting that this model is slighly more accurate. In general, 
linear regression is an easier model to employ and requires fewer
hyperparameters. As a general rule, one should use models which 
achieve the desired level of accuracy with the fewest required user
inputs and the lowest computational cost.

### Resources
1. [Cognite Python SDK Documentation](https://cognite-docs.readthedocs-hosted.com/projects/cognite-sdk-python/en/latest/)
2. [Plotly Dash Documentation and User Guide](https://dash.plotly.com/)
3. [scikit-learn Documentation](https://scikit-learn.org/0.21/documentation.html) 

'''
