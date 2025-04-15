# Windborne  - Atlas Software Intern

- Shipping Delay Forecast <br>
- Deployed via Vercel - https://windborne-atlas.vercel.app/ 

## About Shipping Delayy Forecast
Shipping Delays are quite common in the supply chain industry and this is when I thought that Windborne's technology and API can be used to analyze trade routes and predict whether or not a route would experience shipping delay based on the weather conditions in that particular region. I have sliced the json response so that it contains only first 10 places since it hits my openweather api call limit. Finally it predicts whether a route will experience shipping delay or not based on certain conditions. (I have hardcoded the conditions as of now for testing.)

## API's Used
- Windborne's Treasure JSON
- OpenWeather API - To get the temperature data
- OpenCage API - To reverse Geocode using ```lat and long``` from Windborne's Treasure
- Leaflet (Technically not an API) - For Displaying Map

## Error Handling
- A few of the values i.e. 04,06 etc. json files returns a ```404 Error``` and there were a few methods I tried in order to get the result. 
- Mean - In case 04.json had a 404 Error I tried to get 03.json and 05.json values and averaged it. This doesn't particularly work if 20,21,22,23.json respond with a 404 error. 
- Recursive Search - In case 12,13,14.json had a 404 error and I tried querying 13.json it would get the average of 12 and 14 which would in turn get its response from 11 and 15. 
- Final Solution - Returned a response code different than 200 that triggered the front end to display a message that said Data Unavailable for this particular time. 

## System Design

- The entire system is designed using ```FastAPI``` (Python backend) since it supports high performace and provides API auto documentation (can be accessed here - https://windborne-atlas.vercel.app/docs).
- `FrontEnd Form Input`->   `Backend call`->  `WindBorne Treasure` -> `OpenWeather` -> `OpenCage` -> `Leaflet` - > `Frontend`

## To reproduce the application

- Clone the repository and cd into it.
- Activate your virtualenv and run ```pip install -r requirements.txt```
- make an .env file and add your API keys. 
```
OPENWEATHER_API_KEY=<YOUR KEY>
OPENCAGE_API_KEY=<YOUR_KEY>
```
- run the application using ```uvicorn main:app --host 0.0.0.0 --port 80```


> 
