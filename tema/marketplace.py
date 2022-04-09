"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import RLock

class Marketplace:
    """
    Class that represents the Marketplace. It's the central part of the implementation.
    The producers and consumers use its methods concurrently.
    """
    def __init__(self, queue_size_per_producer):
        """
        Constructor
        
        :type queue_size_per_producer: Int
        :param queue_size_per_producer: the maximum size of a queue associated with each producer
        """
        self.queue_size_per_producer = queue_size_per_producer;
        self.producer_size = 0
        self.consumer_size = 0
        self.lock = RLock()
        self.carts = []
        self.shop_items = []
        self.products_from_producer = []
        

    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """
        self.lock.acquire()
        var = self.producer_size
        self.producer_size += 1
        self.products_from_producer.append(0)
        self.lock.release()
        return var

    def publish(self, producer_id, product):
        """
        Adds the product provided by the producer to the marketplace

        :type producer_id: String
        :param producer_id: producer id

        :type product: Product
        :param product: the Product that will be published in the Marketplace

        :returns True or False. If the caller receives False, it should wait and then try again.
        """
        if self.products_from_producer[producer_id] == self.queue_size_per_producer:
            return False
        else: 
            prod = {}
            prod["id"] = producer_id
            prod["product"] = product   
            
            
            self.products_from_producer[producer_id] += 1
            self.shop_items.append(prod)
            return True

    def new_cart(self):
        """
        Creates a new cart for the consumer

        :returns an int representing the cart_id
        """
        self.lock.acquire()
        var = self.consumer_size
        self.consumer_size += 1
        self.carts.append([])
        self.lock.release()
        return var

        

    def add_to_cart(self, cart_id, product):
        """
        Adds a product to the given cart. The method returns

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to add to cart

        :returns True or False. If the caller receives False, it should wait and then try again
        """
        done = 0
        self.lock.acquire()
        for prod in self.shop_items:
            if prod["product"] == product:
                self.carts[cart_id].append(prod)
                done = 1
                self.shop_items.remove(prod)
                break
        self.lock.release()
        if done == 1:
            return True
        else:
            return False

    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to remove from cart
        """
        for prod in self.carts[cart_id]:
            if prod["product"] == product:
                self.shop_items.append(prod)
                self.carts[cart_id].remove(prod)
                break

    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """
        final_list = []
        # print("final")
        for prod in self.carts[cart_id]:
            self.products_from_producer[prod["id"]] -= 1
            final_list.append(prod["product"])

        return final_list
        
