"""
This module represents the Consumer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Thread
import time

class Consumer(Thread):
    """
    Class that represents a consumer.
    """

    def __init__(self, carts, marketplace, retry_wait_time, **kwargs):
        """
        Constructor.

        :type carts: List
        :param carts: a list of add and remove operations

        :type marketplace: Marketplace
        :param marketplace: a reference to the marketplace

        :type retry_wait_time: Time
        :param retry_wait_time: the number of seconds that a producer must wait
        until the Marketplace becomes available

        :type kwargs:
        :param kwargs: other arguments that are passed to the Thread's __init__()
        """
        Thread.__init__(self, **kwargs)

        self.carts = carts
        self.marketplace = marketplace
        self.retry_wait_time = retry_wait_time
        self.kwargs = kwargs

    def run(self):

        for cart in self.carts:
            # print('Hello consumer! ' , cart)
            consumer_id = self.marketplace.new_cart()
            for product in cart:
                size = product["quantity"]
                if product["type"] == "add":
                    while size > 0:
                        if self.marketplace.add_to_cart(consumer_id, product["product"]) is True: 
                            size -= 1
                            # print("luat")
                        else:
                            # print("nu")
                            time.sleep(self.retry_wait_time)

                else:
                    while size > 0:
                        self.marketplace.remove_from_cart(consumer_id, product["product"])
                        size -= 1
                        # print("sterg")
                    
            # print("gata")
            final_products = self.marketplace.place_order(consumer_id) 
            for product in final_products:
                print(self.kwargs['name'], "bought", product, flush=True)

