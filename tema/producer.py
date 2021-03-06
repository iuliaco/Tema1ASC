"""
This module represents the Producer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Thread
import time


class Producer(Thread):
    """
    Class that represents a producer.
    """

    def __init__(self, products, marketplace, republish_wait_time, **kwargs):
        """
        Constructor.

        @type products: List()
        @param products: a list of products that the producer will produce

        @type marketplace: Marketplace
        @param marketplace: a reference to the marketplace

        @type republish_wait_time: Time
        @param republish_wait_time: the number of seconds that a producer must
        wait until the marketplace becomes available

        @type kwargs:
        @param kwargs: other arguments that are passed to the Thread's __init__()
        """

        Thread.__init__(self, **kwargs)

        self.products = products
        self.marketplace = marketplace
        self.republish_wait_time = republish_wait_time
        self.kwargs = kwargs

    """
    Asignez producatorului un id si cat timp mai sunt consumeri iterez prin lista
    cu produsele mele si adaug produsul in supermarket de cate ori scrie in cantitate
    iar daca nu mai pot astept ca sa vad daca intre timp mi se elibereaza vreun loc
    """

    def run(self):
        producer_id = self.marketplace.register_producer()
        while self.kwargs['daemon'] is True:
            for product in self.products:
                count_product = product[1]
                while count_product > 0:
                    if self.marketplace.publish(producer_id, product[0]) is True:
                        count_product -= 1
                        time.sleep(product[2])
                    else:
                        time.sleep(self.republish_wait_time)
