print("_________________SAYAM_________________")
    #  NEXT
print("_ _ _ calculater_ _ _")
num1=float(input("enter first number:"))


num2=float(input("enter second number:"))


num3=float(input("enter third number:")or 0)


num4=float(input("enter forth number:")or 0)


num5=float(input("enter fifth number ")or 0)



#next wark


sum_result=num1+num2+num3+num4+num5
sub_result=num1-num2
mul_result=num1*num2*num3*num4*num5
div_result=num1/num2 if num2!=0 else "cannot div by 0"
pct_result=(num1/num2)*100
ava_result=(num1+num2)/2


#my choice

choice=input("enter choice(1/2/3/4/5/6):")


if choice =='1':
  print("sum:",sum_result)  


elif choice =='2':
  print("sub:",sub_result)


elif choice =='3':
  print("mul:",mul_result)


elif choice =='4':
  print("div:",div_result)


elif choice=='5':
  print("pct:",pct_result)


elif choice =='6':
  print("ava",ava_result)  


 # my first work

#ok over
#next 
