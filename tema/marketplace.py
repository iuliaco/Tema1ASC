"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

import time
from product import *
from threading import RLock
import unittest
import logging
from logging import Formatter
from logging.handlers import RotatingFileHandler
import sys
sys.path.insert(1, './tema/')


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

        """
        Am declarat ceea ce mi s-a cerut, si am mai adaugat un lock
        un contor pentru id uri la consumeri si la produceri, o lista
        cu elementele valabile din shop si un array de arrays pt fiecare cart
        al fiecarui consumer.
        De asemenea am setat loggerul
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
        handler = RotatingFileHandler(
            'marketplace.log', maxBytes=2000, backupCount=10)
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)8s: %(message)s')
        handler.setFormatter(formatter)
        logging.Formatter.converter = time.gmtime
        self.logger.addHandler(handler)

    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """
        """
        am un lock pentru a da la fiecare producer un id unic
        pe care il apelez cand cresc dimensiunea si retin
        id ul curent si il returnez
        De asemenea ii adaug in contorul de produse faptul ca n a produs
        inca niciun produs
        """
        self.logger.info("Entering register_producer function")
        self.lock.acquire()
        var = self.producer_size
        self.producer_size += 1
        self.products_from_producer.append(0)
        self.lock.release()
        self.logger.info(
            "Leaving register_producer function with result %d", var)
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
        """
        Verific daca cumva deja producerul are numarul maxim de elemente in supermarket
        Iar daca nu are, adaug intr-un element de dictionar produsul si id ul producatorului
        si adaug elementul in lista de produse valabile din shop
        """
        self.logger.info(
            "Entering publish function with producer_id=%d and product=%s", producer_id, product)
        if self.products_from_producer[producer_id] == self.queue_size_per_producer:
            self.logger.info("Leaving publish function with result %r", False)
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
        """
        Am un lock pentru consumatori pentru a ma asigura ca returnez id ul corect
        ii creez un cart la consumer in care sa isi puna produsele care este initial gol
        si ii returnez id ul de la cart
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

        """
        Iterez prin produsele din shop cu un lock pentru ca nu vreau ca 2 consumatori sa
        ia acelasi produs in acelasi timp, si in momentul in care il gasesc il scot din lista
        cu lucruri valabile in shop si il adaug la lista de produse a cartului respectiv
        """
        self.logger.info(
            "Entering add_to_cart function with cart_id =%d and product=%s", cart_id, product)

        done = 0
        self.lock.acquire()
        for prod in self.shop_items:
            if prod["product"] == product:
                self.carts[cart_id].append(prod)
                done = 1
                self.shop_items.remove(prod)
                break
        self.lock.release()
        self.logger.info(
            "Leaving add_to_cart function with result %r", bool(done))

        return bool(done)

    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to remove from cart
        """
        """
        Iterez prin produsele din cosul consumatorului curent si
        cand gasesc produsul de sters in adaug inapoi in lista de produse disponibile
        si il scot din cartul acestuia
        """
        self.logger.info(
            "Entering remove_from_cart function with cart_id =%d and product=%s", cart_id, product)
        for prod in self.carts[cart_id]:
            if prod["product"] == product:
                self.shop_items.append(prod)
                self.carts[cart_id].remove(prod)
                break
        self.logger.info("Leaving add_to_cart function")

    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """

        """
        Iterez prin produsele din marketplace si sterg din contorul producatorului
        fiecare produs din cartul respectiv si adaug produsul in lista finala de produse
        pe care o returnez
        """
        self.logger.info(
            "Entering place_order function with cart_id =%d", cart_id)
        final_list = []
        # print("final")
        for prod in self.carts[cart_id]:
            self.products_from_producer[prod["id"]] -= 1
            final_list.append(prod["product"])
        self.logger.info(
            "Leaving place_order function with list: %s", final_list)
        return final_list


class TestMarketplace(unittest.TestCase):
    """
    Clasa de test in care mockuiesc un marketplace si ma folosesc de el
    pentru a testa fiecare functie
    """
    def setUp(self):
        self.marketplace = Marketplace(3)

    """
    Testez inregistrarea producatorilor si ma asigur ca se returneaza mereu id ul corect
    """
    def test_register_producer(self):
        self.assertEqual(self.marketplace.register_producer(), 0)
        self.assertEqual(self.marketplace.register_producer(), 1)
        self.assertEqual(self.marketplace.register_producer(), 2)
        self.assertEqual(self.marketplace.register_producer(), 3)
        self.assertEqual(self.marketplace.register_producer(), 4)
        self.assertEqual(self.marketplace.register_producer(), 5)

    """
    Testez inregistrarea carturilor si ma asigur ca se returneaza mereu id ul corect
    """
    def test_new_cart(self):
        self.assertEqual(self.marketplace.new_cart(), 0)
        self.assertEqual(self.marketplace.new_cart(), 1)
        self.assertEqual(self.marketplace.new_cart(), 2)
        self.assertEqual(self.marketplace.new_cart(), 3)
        self.assertEqual(self.marketplace.new_cart(), 4)
        self.assertEqual(self.marketplace.new_cart(), 5)

    """
    Testez functia de publish, incerc sa postez la un furnizor 4 produse
    cand limita maxima la coada este de 3 ca sa am si caz de true si caz de false
    """
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

    """
    Adaug in magazine 3 produse si incerc sa adaug 3 produse in cart,
    dintre care unul inexistent
    """
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

    """
    Adaug in magazine 3 produse, iau 2 si pun unul inapoi pe raft, si 
    observ ca lungimea cartului consumerului care a realizat actiunea 
    de remove a scazut cu 1
    """
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

    """
    Icerc sa adaug in cos 2 produse si sa ii dau place order si verific ca lista mea
    contine produsele adaugate in cos, si dupa incerc sa fac furnizorul care avea
    produse din cartul meu sa adauge inapoi produse acum ca acesta poate
    """
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
