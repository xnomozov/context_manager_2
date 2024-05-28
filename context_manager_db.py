import os
from typing import Dict, Optional
from dotenv import load_dotenv
import psycopg2
from datetime import datetime
from colorama import Fore

load_dotenv()
data_params: Dict[str, str] = {
    'database': os.getenv('database'),
    'user': os.getenv('user'),
    'password': os.getenv('password'),
    'host': os.getenv('host'),
    'port': os.getenv('port')
}


class ConnectDB:
    def __init__(self, data_attr: Dict[str, str]):
        self.data_attr = data_attr
        self.conn: Optional[psycopg2.extensions.connection] = None
        self.cur: Optional[psycopg2.extensions.cursor] = None

    def __enter__(self) -> psycopg2.extensions.cursor:
        self.conn = psycopg2.connect(**data_params)
        self.cur = self.conn.cursor()
        self.cur.execute("""CREATE TABLE IF NOT EXISTS products(
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        image VARCHAR(255) NOT NULL,
        is_liked BOOLEAN NOT NULL default FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")  # we can add any logic there, and I create table Products
        self.conn.commit()
        return self.cur

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.cur:
            self.cur.close()
        if self.conn:
            if exc_type:
                self.conn.rollback()
            else:
                self.conn.commit()
            self.conn.close()


class Product:
    def __init__(self, name: str, image: str,
                 is_liked: bool = False,
                 created_at: Optional[datetime] = None,
                 updated_at: Optional[datetime] = None) -> None:
        self.name = name
        self.image = image
        self.is_liked = is_liked
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    @staticmethod
    def input_data() -> 'Product':
        name: str = input(Fore.LIGHTWHITE_EX + 'Enter product name: ' + Fore.RESET)
        image: str = input(Fore.LIGHTWHITE_EX + 'Enter product image: ' + Fore.RESET)
        is_liked: bool = input(Fore.LIGHTWHITE_EX + 'Is product liked? 1/2: ' + Fore.RESET) == '1'
        product: Product = Product(name, image, is_liked)
        return product

    @staticmethod
    def insert_data() -> None:
        try:
            with ConnectDB(data_params) as cur:
                product: Product = Product.input_data()
                cur.execute("""
                           INSERT INTO products (name, image, is_liked)
                           VALUES (%s, %s, %s)
                       """, (product.name, product.image, product.is_liked))
                print(Fore.LIGHTGREEN_EX + "Product created successfully." + Fore.RESET)
        except psycopg2.Error as e:
            print(Fore.LIGHTRED_EX + f"Error inserting data: {e}" + Fore.RESET)

    @staticmethod
    def show_data() -> None:
        try:
            with ConnectDB(data_params) as cur:
                cur.execute("SELECT * FROM products")
                list(map(print, (row for row in cur.fetchall())))
        except psycopg2.Error as e:
            print(Fore.LIGHTRED_EX + f"Error fetching data: {e}" + Fore.RESET)

    @staticmethod
    def update_data() -> None:
        try:
            with ConnectDB(data_params) as cur:
                _id: str = input(Fore.LIGHTWHITE_EX + "Insert product ID to update: " + Fore.RESET)
                product: Product = Product.input_data()
                cur.execute("""
                            UPDATE products
                            SET name = %s, image = %s, is_liked = %s, updated_at = CURRENT_TIMESTAMP
                            WHERE id = %s
                        """, (product.name, product.image, product.is_liked, _id))
                print(Fore.LIGHTGREEN_EX + "Product updated successfully." + Fore.RESET)
        except psycopg2.Error as e:
            print(Fore.LIGHTRED_EX + f"Error updating data: {e}" + Fore.RESET)

    @staticmethod
    def delete_data() -> None:
        try:
            with ConnectDB(data_params) as cur:
                Product.show_data()
                _id: str = input(Fore.LIGHTWHITE_EX + "Insert product ID to delete: " + Fore.RESET)
                cur.execute("DELETE FROM products WHERE id = %s", (_id,))
                print(Fore.LIGHTGREEN_EX + "Product deleted successfully." + Fore.RESET)
        except psycopg2.Error as e:
            print(Fore.LIGHTRED_EX + f"Error deleting data: {e}" + Fore.RESET)

    @staticmethod
    def menu() -> str:
        print(Fore.LIGHTWHITE_EX + """
            Welcome to Product Management
            What would you like to do?
            1. Add product
            2. Delete product
            3. Show products
            4. Update product
            0. Exit
            """ + Fore.RESET)
        return input(Fore.LIGHTWHITE_EX + "Enter your choice: " + Fore.RESET)

    @staticmethod
    def run() -> None:
        choices: Dict[str, callable] = {
            '1': Product.insert_data,
            '2': Product.delete_data,
            '3': Product.show_data,
            '4': Product.update_data,
            '0': lambda: print(Fore.LIGHTGREEN_EX + "Thank you for using Product Management" + Fore.RESET)
        }

        while True:
            choice: str = Product.menu()
            action: callable = choices.get(choice)
            if action:
                if choice == '0':
                    action()
                    break
                else:
                    action()
            else:
                print(Fore.LIGHTRED_EX + "Invalid choice, please try again" + Fore.RESET)


if __name__ == '__main__':
    Product.run()
