#using Python 3 image as launching point
FROM python:3

#add source folder
COPY . /.

#install dependencies
RUN pip install -r requirements.txt

#run bot
CMD [ "python", "./main.py" ]
