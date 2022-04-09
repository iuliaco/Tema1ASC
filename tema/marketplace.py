"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from pickle import FALSE
from threading import RLock
from tkinter.tix import Tree
import unittest
import logging
from logging import Formatter
from logging.handlers import RotatingFileHandler
import sys
sys.path.insert(1, './tema/')
# from . import *
from product import *
import time

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
        self.queue_size_per_producer = queue_size_per_producer
        self.producer_size = 0
        self.consumer_size = 0
        self.lock = RLock()
        self.carts = []
        self.shop_items = []
        self.products_from_producer = []
        self.logger = logging.getLogger('marketplace')
        self.logger.setLevel(logging.INFO)
        handler = RotatingFileHandler('marketplace.log', maxBytes=2000, backupCount=10)
        formatter = logging.Formatter('%(asctime)s %(levelname)8s: %(message)s')
        handler.setFormatter(formatter)
        logging.Formatter.converter = time.gmtime
        self.logger.addHandler(handler)



    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """
        self.logger.info("Entering register_producer function")
        self.lock.acquire()
        var = self.producer_size
        self.producer_size += 1
        self.products_from_producer.append(0)
        self.lock.release()
        self.logger.info("Leaving register_producer function with result %d", var)
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
        self.logger.info("Entering publish function with producer_id=%d and product=%s")
        if self.products_from_producer[producer_id] == self.queue_size_per_producer:
            self.logger.info("Leaving publish function with result %r", FALSE)
            return False
        else:
            prod = {}
            prod["id"] = producer_id
            prod["product"] = product

            self.products_from_producer[producer_id] += 1
            self.shop_items.append(prod)
            self.logger.info("Leaving publish function with result %r", True)
            return True

    def new_cart(self):
        """
        Creates a new cart for the consumer

        :returns an int representing the cart_id
        """
        self.logger.info("Entering new_cart function")
        self.lock.acquire()
        var = self.consumer_size
        self.consumer_size += 1
        self.carts.append([])
        self.lock.release()
        self.logger.info("Leaving new_cart function with result %d", var)
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
        return bool(done)

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


class TestMarketplace(unittest.TestCase):
    def setUp(self):
        self.marketplace = Marketplace(3)

    def test_register_producer(self):
        self.assertEqual(self.marketplace.register_producer(), 0)
        self.assertEqual(self.marketplace.register_producer(), 1)
        self.assertEqual(self.marketplace.register_producer(), 2)
        self.assertEqual(self.marketplace.register_producer(), 3)
        self.assertEqual(self.marketplace.register_producer(), 4)
        self.assertEqual(self.marketplace.register_producer(), 5)

    def test_new_cart(self):
        self.assertEqual(self.marketplace.new_cart(), 0)
        self.assertEqual(self.marketplace.new_cart(), 1)
        self.assertEqual(self.marketplace.new_cart(), 2)
        self.assertEqual(self.marketplace.new_cart(), 3)
        self.assertEqual(self.marketplace.new_cart(), 4)
        self.assertEqual(self.marketplace.new_cart(), 5)

    def test_publish(self):
        self.assertEqual(self.marketplace.register_producer(), 0)
        self.assertEqual(self.marketplace.register_producer(), 1)
        self.assertEqual(self.marketplace.new_cart(), 0)
        self.assertTrue(self.marketplace.publish(
            1, Tea(name='White Peach', price=5, type='White')))
        self.assertTrue(self.marketplace.publish(
            1, Coffee(name='Brasil', price=7, acidity=5.09, roast_level='MEDIUM')))
        self.assertTrue(self.marketplace.publish(
            1, Tea(name='English Breakfast', price=2, type='Black')))
        self.assertFalse(self.marketplace.publish(
            1, Coffee(name='Indonezia', price=1, acidity=5.05, roast_level='MEDIUM')))

    def test_add_to_cart(self):
        self.assertEqual(self.marketplace.register_producer(), 0)
        self.assertEqual(self.marketplace.register_producer(), 1)
        self.assertEqual(self.marketplace.new_cart(), 0)
        self.assertTrue(self.marketplace.publish(
            1, Tea(name='White Peach', price=5, type='White')))
        self.assertTrue(self.marketplace.publish(
            1, Coffee(name='Brasil', price=7, acidity=5.09, roast_level='MEDIUM')))
        self.assertTrue(self.marketplace.publish(
            1, Tea(name='English Breakfast', price=2, type='Black')))
        self.assertFalse(self.marketplace.publish(
            1, Coffee(name='Indonezia', price=1, acidity=5.05, roast_level='MEDIUM')))
        self.assertTrue(self.marketplace.add_to_cart(
            0, Coffee(name='Brasil', price=7, acidity=5.09, roast_level='MEDIUM')))
        self.assertFalse(self.marketplace.add_to_cart(
            0, Coffee(name='Brasil', price=7, acidity=5.09, roast_level='MEDIUM')))

    def test_remove_from_cart(self):
        self.assertEqual(self.marketplace.register_producer(), 0)
        self.assertEqual(self.marketplace.register_producer(), 1)
        self.assertEqual(self.marketplace.new_cart(), 0)
        self.assertTrue(self.marketplace.publish(
            1, Tea(name='White Peach', price=5, type='White')))
        self.assertTrue(self.marketplace.publish(
            1, Coffee(name='Brasil', price=7, acidity=5.09, roast_level='MEDIUM')))
        self.assertTrue(self.marketplace.publish(
            1, Tea(name='English Breakfast', price=2, type='Black')))
        self.assertFalse(self.marketplace.publish(
            1, Coffee(name='Indonezia', price=1, acidity=5.05, roast_level='MEDIUM')))
        self.assertTrue(self.marketplace.add_to_cart(
            0, Coffee(name='Brasil', price=7, acidity=5.09, roast_level='MEDIUM')))
        self.assertTrue(self.marketplace.add_to_cart(
            0, Tea(name='English Breakfast', price=2, type='Black')))
        self.assertFalse(self.marketplace.add_to_cart(
            0, Coffee(name='Brasil', price=7, acidity=5.09, roast_level='MEDIUM')))
        self.assertEqual(len(self.marketplace.carts[0]), 2)
        self.marketplace.remove_from_cart(
            0, Coffee(name='Brasil', price=7, acidity=5.09, roast_level='MEDIUM'))
        self.assertEqual(len(self.marketplace.carts[0]), 1)

    def test_place_order(self):
        self.assertEqual(self.marketplace.register_producer(), 0)
        self.assertEqual(self.marketplace.register_producer(), 1)
        self.assertEqual(self.marketplace.new_cart(), 0)
        self.assertTrue(self.marketplace.publish(
            1, Tea(name='White Peach', price=5, type='White')))
        self.assertTrue(self.marketplace.publish(
            1, Coffee(name='Brasil', price=7, acidity=5.09, roast_level='MEDIUM')))
        self.assertTrue(self.marketplace.publish(
            1, Tea(name='English Breakfast', price=2, type='Black')))
        self.assertFalse(self.marketplace.publish(
            1, Coffee(name='Indonezia', price=1, acidity=5.05, roast_level='MEDIUM')))
        self.assertTrue(self.marketplace.add_to_cart(
            0, Coffee(name='Brasil', price=7, acidity=5.09, roast_level='MEDIUM')))
        self.assertTrue(self.marketplace.add_to_cart(
            0, Tea(name='English Breakfast', price=2, type='Black')))
        self.assertFalse(self.marketplace.add_to_cart(
            0, Coffee(name='Brasil', price=7, acidity=5.09, roast_level='MEDIUM')))
        self.assertEqual(len(self.marketplace.carts[0]), 2)
        self.marketplace.remove_from_cart(
            0, Coffee(name='Brasil', price=7, acidity=5.09, roast_level='MEDIUM'))
        self.assertEqual(len(self.marketplace.carts[0]), 1)
        self.assertTrue(self.marketplace.add_to_cart(
            0, Tea(name='White Peach', price=5, type='White')))
        list = [Tea(name='English Breakfast', price=2, type='Black'),
                Tea(name='White Peach', price=5, type='White')]
        self.assertEqual(self.marketplace.place_order(0), list)
        self.assertTrue(self.marketplace.publish(
            1, Coffee(name='Indonezia', price=1, acidity=5.05, roast_level='MEDIUM')))
