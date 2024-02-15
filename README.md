<h1>U.S. County-Level Data Retrieval from the ACS-5 API & Basic Data Exploration</h1>


<h2>Description</h2>
<b>This project stems from my master’s thesis research, which involved conducting Exploratory Spatial Data Analysis (ESDA) of county level ACS-5 data. Throughout this process, a significant observation emerged: notable disparities exist in the data quality across various regions and variables. A prevailing trend indicates that sparsely populated counties and more specialized variables tend to exhibit lower data quality. To comprehensively understand data quality, streamline the creation of a geoJSON data frame, and gain insights into variables (spatial) distributions and relationships, four distinct functions were developed.
</b>
<br />
<br />
The initial function serves as the primary tool for users, facilitating the retrieval of county-level data from the ACS-5 API. It provides insights into data quality while seamlessly generating a geoJSON data frame. Function 2 automates the creation of boxplots, offering visual representations of the data's distribution. Function 3 generates a scatterplot matrix, allowing users to explore bivariate relationships among variables. Lastly, function 4 produces basic maps displaying variable values for each county across the contiguous USA, Alaska, Hawaii, and Puerto Rico.
<br />
<br />
There are three prerequisites necessary for the proper functioning of the code:

1.)	A valid API Key.

2.)	A corresponding shapefile for the requested years.

3.)	While not mandatory for the functionality of the functions, possessing a basic understanding of ACS-5 is highly beneficial.

Once these preliminary steps are satisfied, you can proceed to visit https://api.census.gov/data/2019/acs/acs5/subject/variables.json (adjusting the year as needed) to select and explore the variables of interest. 

<br />
<br />

$\[ \text{Percent of CVs>30} = \frac{\text{Count of CVs>30}}{\text{Count of Estimates not zero or missing}} \times 100 \]$
