# GimmeShelter
## A Flask app to predict adoption time for dogs in US shelters

This website implemented in this project is available at www.gimmeadogshelter.com.

Data source: I queried the Petfinder.com API were to identify ~42,000 dogs that were adopted. Next,  I trained a Random Forest classifier using characteristics of those dogs (location, size, breed, sex, age, urban vs. rural listing area, etc.) as well as the text descriptions to predict adoption time. This model is then used to generate predictions which enable adoption agencies to determine how long it will take their dogs to be adopted. Exploratory data analysis is also implemented to allow users to visualize adoption times for dogs in different categories. See the slides linked in [about this project](www.gimmeadogshelter.com/about) for more information, or contact me at nicholas.r.weir@gmail.com.

To use: visit www.gimmeadogshelter.com to see the product in action. If you would like to implement part of this repository yourself, contact me.

This app is the result of an Insight Health Data Science Fellowship (Boston 18B) project.
