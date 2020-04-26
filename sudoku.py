import cv2
import boto3
import csv
from flask import Flask
from flask import render_template
from flask import request
import os

import numpy as np
SUDOKU_FOLDER = os.path.join('static', 'sudoku')
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = SUDOKU_FOLDER




@app.route('/', methods = ['POST','GET'])
def home():

    return render_template('home.html')


@app.route('/solution', methods = ['POST'])
def solution():
    if request.method == 'POST':
        f = request.files['file']
        f.save(f.filename)
        path=str(f.filename)
        #return render_template("solution.html", name = f.filename)

    with open('E:\credentials.csv') as input:
        next(input)
        reader=csv.reader(input)
        for line in reader:
            access_key_id=line[2]
            secret_access_key=line[3]

    client = boto3.client('rekognition',
                          aws_access_key_id=access_key_id,
                          aws_secret_access_key=secret_access_key,
                          region_name='ap-south-1')


    img=cv2.imread(path)

    _,th=cv2.threshold(img,127,255,cv2.THRESH_BINARY)
    s=th.shape
    l=s[0]
    b=s[1]
    sudoku=-np.ones((9,9),dtype='int')
    test_image=np.ones((128,128,3),dtype=np.uint8)

    #print(sudoku)
    number_of_given_numbers=0
    for i in range(0,9):
      for j in range(0,9):
        roi=th[i*(l//9) + 6 : i*(l//9) +l//9 -6  ,  j*(b//9) +6 : j*(b//9) + b//9 -6]
        a1=roi.shape[0]
        b1=roi.shape[1]
        #print(a1,b1)

        roi1=roi[int(0.2*a1) : int(0.8*a1) ,  int(0.2*b1) : int(0.8*b1)]
        '''print(roi1.shape,roi.shape)
        cv2.imshow('roi',roi1)
        cv2.waitKey(0)
        cv2.destroyAllWindows()'''



        test=cv2.resize(roi1,(128,128))

        test=cv2.subtract(255,test)
        if((test==0).all()):
            sudoku[i,j]=0
        else:
            number_of_given_numbers+=1
            pass





    with open(path,'rb')as input:
        test=input.read()



    numbers=[]
    response = client.detect_text(Image={'Bytes': test})
    for label in response['TextDetections']:
        #print ("Label: " + label['DetectedText'])
        label=label['DetectedText']
        numbers.append(label)

    #sudoku_numbers=numbers[len(numbers)-number_of_given_numbers:]
    print(numbers)
    print(numbers)
    sudoku_numbers=[]

    for var in numbers:
        res=list(var)

        for j in res:

            if(j.isdigit()):
                sudoku_numbers.append(int(j))
        if(len(sudoku_numbers)==number_of_given_numbers):
            break

    print(sudoku_numbers)

    k=0
    for i in range(0,9):
        for j in range(0,9):
            if(sudoku[i,j]==-1):
                sudoku[i,j]=int(sudoku_numbers[k])
                k+=1




    print(sudoku)
    solution_of_sudoku=solve_the_grid(sudoku)
    print("SOLUTION IS  ",solution_of_sudoku)
    if(solution_of_sudoku=="NO SOLUTION"):
        return render_template('error.html')

    else:
        return render_template('solution.html',solution_of_sudoku=solution_of_sudoku)



def solve_the_grid(sudoku):
    def print_grid(arr):
        for i in range(9):
            for j in range(9):
                print(arr[i][j])
            print ('\n')

    def find_empty_location(arr,l):
        for row in range(9):
            for col in range(9):
                if(arr[row][col]==0):
                    l[0]=row
                    l[1]=col
                    return True
        return False

    def used_in_row(arr,row,num):
        for i in range(9):
            if(arr[row][i] == num):
                return True
        return False

    def used_in_col(arr,col,num):
        for i in range(9):
            if(arr[i][col] == num):
                return True
        return False

    def used_in_box(arr,row,col,num):
        for i in range(3):
            for j in range(3):
                if(arr[i+row][j+col] == num):
                    return True
        return False

    def check_location_is_safe(arr,row,col,num):

        # Check if 'num' is not already placed in current row,
        # current column and current 3x3 box
        return not used_in_row(arr,row,num) and not used_in_col(arr,col,num) and not used_in_box(arr,row - row%3,col - col%3,num)


    def solve_sudoku(arr):

        # 'l' is a list variable that keeps the record of row and col in find_empty_location Function
        l=[0,0]

        # If there is no unassigned location, we are done
        if(not find_empty_location(arr,l)):
            return True

        # Assigning list values to row and col that we got from the above Function
        row=l[0]
        col=l[1]

        # consider digits 1 to 9
        for num in range(1,10):

            # if looks promising
            if(check_location_is_safe(arr,row,col,num)):

                # make tentative assignment
                arr[row][col]=num

                # return, if success, ya!
                if(solve_sudoku(arr)):
                    return True

                # failure, unmake & try again
                arr[row][col] = 0

        # this triggers backtracking
        return False

    if __name__=="__main__":

        arr=sudoku

        # if success print the grid
        if(solve_sudoku(arr)):
            #print_grid(arr)
            return(arr)

        else:

            print("No solution exists")
            return("NO SOLUTION")




#############################################################################



if __name__ == '__main__':
    app.run(debug=True)
