NEXT STEPS
Create a DB with locations to extract
    - Lat
    - Long
    - Timezone

IDEA
   - Before workflow
    - Run the feed
    - Run the main to 100 rows and see if works good
    - Test fails cases(api blocks)
        - No data pipeline error
        - Error but with some data ok (define a number 500/600 ok, lower the pipeline fails )
    - Run the full data collector and see if is good
    - Check if the API reset on midnight or 24 after block 
   - WORKFLOW
        - Copy the create volume to repo
        - Commit the logs and data
        - Output something to use on pipeline no know if the script end right or not
    - Call the main.py between 4pm and 6pm
        - Update the main.py script to save the data when get error, not only the error
        - Call until get a error
            - probably will be the Error: 400 - {"status":400,"code":204,"message":"Exceeded daily quota"}
            - On pipeline i will get error only if there is any data
    - Save da SQL lite db on data/
    - After a week merge the data set and try to create a model
    - Continue extract data
    Notes: The data will be for today and next 2 days, so i can see i accuracy the third party is as the sunset is close.