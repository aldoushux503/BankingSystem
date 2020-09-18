import random
import sqlite3


class DataBasesCard:
    """
    The class that manages the connection and table creation
    """
    db_file = 'card.s3db'

    @staticmethod
    def main():
        """
        The main from which the connection and the table are created
        """
        # create a database connection
        conn = DataBasesCard.create_connection()

        # create tables
        if conn is not None:
            # create card table
            DataBasesCard.create_table(conn)
        else:
            print("Error! cannot create the database connection.")

    @staticmethod
    def create_connection():
        """
        Create a database connection to the SQLite database
        specified by DataBasesCard.db_file
        """
        conn = None
        try:
            conn = sqlite3.connect(DataBasesCard.db_file)
            return conn
        except sqlite3.Error as e:
            print(e)

        return conn

    @staticmethod
    def create_table(conn):
        """
        Create a table from the sql_create_card_table statement
        """

        sql_create_card_table = """ CREATE TABLE IF NOT EXISTS card (
                                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                number TEXT,
                                                pin TEXT,
                                                balance INTEGER DEFAULT 0
                                            ); """

        try:
            c = conn.cursor()
            c.execute(sql_create_card_table)
        except sqlite3.Error as e:
            print(e)


class Bank:
    def __init__(self):
        self.conn = DataBasesCard.create_connection()  # get a database connection

    def menu(self):
        """
        Menu Banking System
        """
        while True:
            print("1. Create an account",
                  "2. Log into account",
                  "0. Exit", sep="\n")

            choice = input()

            if choice == "1":
                self.create_account()
            elif choice == "2":
                self.log_account()
            elif choice == "0":
                print("Bye!")
                exit()
            else:
                print("There is no such option, try again")

    def create_account(self):
        """
        Create customer account:
        0. Creates a card number using the algorithm Luhn
        1. Create PIN number
        2. Add data to the database card.s3db -> table card
        """
        card_number = self.algorithm_luhn()  # Generate random card
        pin_number = ''.join([str(random.randint(0, 9)) for _ in range(4)])  # Generate PIN code

        print("\nYour card has been created",
              "Your card number:", f"{card_number}",
              "Your card PIN:", f"{pin_number}\n", sep="\n")

        # Add new bank account  to the table card
        card_data = (card_number, pin_number)
        self.add_into_table(self.conn, card_data)

    def log_account(self):
        """
        Customer logging
        0. Check user entered card number and pin from the databases
        """
        card_number = input('\nEnter your card number:\n')
        pin_number = input("Enter your PIN:\n")

        check = self.login_customer(self.conn, card_number, pin_number)

        if check:
            print("You have successfully logged in!")
            self.operation_card(card_number)
        else:
            print("Wrong card number or PIN!")

    @staticmethod
    def algorithm_luhn(card_number=None):
        """
        Create or check card number using algorithm_luhn
        0. If the card number was passed to the function
           the last digit is truncated and checks the number for veracity
        1. Else last digit is truncated and created try card number
        2. multiply numbers by 2, if number > 9 subtracts from 9
        3. get the sum of all numbers
        4. add 1 while sum % 10 == 0
        5. add the number to the end
        """
        if not bool(card_number):
            card_number = [4, 0, 0, 0, 0, 0]
            card_number += [random.randint(0, 9) for _ in range(10)]

        card_number.pop()
        lun_alg = card_number[:]

        # Algorithm
        for i in range(0, len(card_number), 2):
            number_multi = lun_alg[i] * 2
            if number_multi > 9:
                lun_alg[i] = number_multi - 9
            else:
                lun_alg[i] = number_multi

        sum_lun_alg = sum(lun_alg)
        i = 0

        while sum_lun_alg % 10 != 0:
            sum_lun_alg += 1
            i += 1

        card_number.append(i)
        return "".join(map(str, card_number))

    @staticmethod
    def add_into_table(conn, card_data):
        """
        Adds to the table 'card' new customer's (card number and PIN)
        """
        sql = ''' INSERT INTO card(number, pin)
                  VALUES(?,?) '''

        cur = conn.cursor()
        cur.execute(sql, card_data)
        conn.commit()

    @staticmethod
    def login_customer(conn, card_number, card_pin):
        """
        Checks if such card number and PIN are in the table 'card'
        """
        sql = ''' SELECT number, pin FROM card WHERE number = ? and pin = ?'''

        cur = conn.cursor()
        cur.execute(sql, (card_number, card_pin))
        return bool(cur.fetchone())  # Returns True or False

    def operation_card(self, card_number):
        """
        Menu operation with card
        """
        while True:
            print("\n1. Balance",
                  "2. Add income",
                  "3. Do transfer",
                  "4. Close account",
                  "5. Log out",
                  "0. Exit", sep="\n")

            choice = input()

            if choice == "1":
                self.check_balance(self.conn, card_number, Text=True)
            elif choice == "2":
                amount = float(input("Enter income:\n"))
                self.add_income(self.conn, amount, card_number)
            elif choice == "3":
                self.transfer(card_number)
            elif choice == "4":
                self.close_account(self.conn, card_number)
                break
            elif choice == "5":
                print("You have successfully logged out!")
                break
            elif choice == "0":
                print("Bye!")
                exit()
            else:
                print("There is no such option, try again")

    @staticmethod
    def check_balance(conn, card_number, Text=None):
        """
        Checks the balance on the card
        """
        sql = '''SELECT balance FROM card WHERE number = ?'''

        cur = conn.cursor()
        cur.execute(sql, [card_number])

        try:
            amount = cur.fetchone()[0]
        except TypeError:
            return 'False'
        else:
            if bool(Text):
                print("Balance: {}".format(amount))
            else:
                return amount

    @staticmethod
    def add_income(conn, amount, card_number, transfer_card=None):
        """
        Adds an amount of money to the customer's account
        Or transfer from one account to another
        """
        sql = '''UPDATE card SET balance = balance + ? WHERE number = ?;'''
        sql_transfer = '''UPDATE card SET balance = balance - ? WHERE number = ?'''

        cur = conn.cursor()

        if not transfer_card:
            cur.execute(sql, (amount, card_number))
            conn.commit()
            print("Income was added!")
        else:
            cur.execute(sql_transfer, (amount, card_number))
            cur.execute(sql, (amount, transfer_card))

            conn.commit()
            print("Success!")

    def transfer(self, card_number):
        print("\nTransfer")
        transfer_card = input("Enter card number:\n")

        # Checks if the card number matches the algorithm Luhn
        if transfer_card != self.algorithm_luhn(list(map(int, transfer_card))):
            print("Probably you made a mistake in the card number. Please try again!")
        # Checks card number in database
        elif self.check_balance(self.conn, transfer_card) == 'False':
            print("Such a card does not exist.")
        elif card_number == transfer_card:
            print("You can't transfer money to the same account!")
        else:
            amount = float(input("Enter how much money you want to transfer:\n"))
            if amount > self.check_balance(self.conn, card_number):
                print("Not enough money!")
            else:
                self.add_income(self.conn, amount, card_number, transfer_card)

    @staticmethod
    def close_account(conn, card_number):
        """
        Closes the customer's account
        """
        sql = '''DELETE FROM card WHERE number = ?'''

        cur = conn.cursor()
        cur.execute(sql, [card_number])
        conn.commit()
        print("The account has been closed!")


if __name__ == '__main__':
    DataBasesCard.main()
    Bank().menu()
