from datetime import datetime
from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse
from pymongo import MongoClient

cluster = MongoClient("mongodb+srv://admin:admin@cluster0.xzkll9b.mongodb.net/?retryWrites=true&w=majority")
db = cluster["bakery"]
users = db["users"]
orders = db["orders"]

app = Flask(__name__)


@app.route('/main', methods=['get', 'post'])
def main():
    text = request.form.get("Body")
    number = request.form.get("From")
    resp = MessagingResponse()
    msg = resp.message()

    user = users.find_one({"number": number})

    if bool(user) == False:
        msg.media("https://i.ibb.co/BPKnXVP/Red-Velvet-Cake-Waldorf-Astoria.jpg")
        msg.body("Hi, thanks for contacting *The Red Velvet*."
                 "\nYou can choose from one of the options below: "
                 "\n\n*Type*\n"
                 "\n 1️⃣ To *contact* us "
                 "\n 2️⃣ To *order* snacks "
                 "\n 3️⃣ To know our *working hours* "
                 "\n 4️⃣ To get our *address*")
        users.insert_one({"number": number, "status": "main", "messages": []})

    elif user["status"] == "main":
        try:
            option = int(text)
        except:
            msg.body("Please Enter a valid response")
            return Response(str(resp), mimetype="application/xml")

        # Contact
        if option == 1:
            msg.body("You can contact us through phone or e-mail.\n"
                     "\n*Phone*: 991234 56789 "
                     "\n*E-mail* : contact@theredvelvet.io")

        # Ordering
        elif option == 2:
            users.update_one({"number": number}, {"$set": {"status": "ordering"}})
            msg.body("You can select one of the following cakes to order: \n"
                     "\n1️⃣ Red Velvet  "
                     "\n2️⃣ Dark Forest "
                     "\n3️⃣ Ice Cream Cake"
                     "\n4️⃣ Plum Cake "
                     "\n5️⃣ Sponge Cake "
                     "\n6️⃣ Genoise Cake "
                     "\n7️⃣ Angel Cake "
                     "\n8️⃣ Carrot Cake "
                     "\n9️⃣ Fruit Cake  "
                     "\n0️⃣ Go Back")
            
        # Working Hourse
        elif option == 3:
            msg.body("We work from *9 a.m. to 5 p.m*.")

        # Address
        elif option == 4:
            msg.body("We have multiple stores across the city. "
                     "Our main center is at *4/54, New Delhi*")

        else:
            msg.body("Please enter a valid response")

    elif user["status"] == "ordering":
        try:
            option = int(text)
        except:
            msg.body("Please enter a valid response")
            return Response(str(resp), mimetype="application/xml")

        if option == 0:  # Back
            users.update_one({"number": number}, {"$set": {"status": "main"}})
            msg.body("You can choose from one of the options below: "
                     "\n\n*Type*\n"
                     "\n 1️⃣ To *contact* us "
                     "\n 2️⃣ To *order* snacks "
                     "\n 3️⃣ To know our *working hours* "
                     "\n 4️⃣ To get our *address*")

        elif 1 <= option <= 9:
            cakes = ["Red Velvet Cake",
                     "Dark Forest Cake",
                     "Ice Cream Cake",
                     "Plum Cake",
                     "Sponge Cake",
                     "Genoise Cake",
                     "Angel Cake",
                     "Carrot Cake",
                     "Fruit Cake"]
            selected = cakes[option - 1]
            users.update_one(
                {"number": number}, {"$set": {"status": "address"}})
            users.update_one(
                {"number": number}, {"$set": {"item": selected}})
            msg.body("Excellent choice 😉")
            msg.body("Please enter your address to confirm the order")

        else :
            msg.body("Please enter a valid response")

    elif user["status"] == "address":
        selected = user["item"]
        msg.body("Thank you for shopping with us 😀")
        msg.body(f"Your order for *{selected}* has been recieved and will be delivered soon")
        orders.insert_one({"number": number, "item": selected, "address": text, "order_time": datetime.now()})
        users.update_one({"number": number}, {"$set": {"status": "ordered"}})

    elif user["status"] == "ordered":
        msg.body("Hi, thanks for contacting again."
                 "\nYou can choose from one of the options below: "
                 "\n*Type*\n"
                 "\n 1️⃣ To *contact* us "
                 "\n 2️⃣ To *order* snacks "
                 "\n 3️⃣ To know our *working hours* "
                 "\n 4️⃣ To get our *address*")
        users.update_one({"number": number}, {"$set": {"status": "main"}})

    users.update_one({"number": number}, {"$push": {"messages": {"text": text, "date": datetime.now()}}})

    return Response(str(resp), mimetype="application/xml")


if __name__ == '__main__':
    app.run()
