import pytest
from unittest.mock import PropertyMock, patch
from typing import List
from timeit import repeat
from functools import partial

from bots.fall_challenge_2023.game_loop import GameLoop


BOT_PACKAGE = "bots.fall_challenge_2023"
GameLoop.LOG = False

TEST_INPUTS = [
    (['14', '4 0 0', '5 1 0', '6 0 1', '7 1 1', '8 0 2', '9 1 2', '10 2 0', '11 3 0', '12 2 1', '13 3 1', '14 2 2', '15 3 2', '16 -1 -1', '17 -1 -1'],
     1, ['0', '0', '0', '0', '2', '0 2000 500 0 30', '2 6000 500 0 30', '2', '1 7999 500 0 30', '3 3999 500 0 30', '0', '0', '28', '0 4 BR', '0 5 BR', '0 6 BR', '0 7 BR', '0 8 BR', '0 9 BR', '0 10 BL', '0 11 BR', '0 12 BR', '0 13 BR', '0 14 BR', '0 15 BR', '0 16 BL', '0 17 BR', '2 4 BR', '2 5 BL', '2 6 BR', '2 7 BL', '2 8 BL', '2 9 BR', '2 10 BL', '2 11 BR', '2 12 BR', '2 13 BL', '2 14 BL', '2 15 BR', '2 16 BL', '2 17 BR']),
    (['18', '4 0 0', '5 1 0', '6 0 1', '7 1 1', '8 0 2', '9 1 2', '10 2 0', '11 3 0', '12 2 1', '13 3 1', '14 2 2', '15 3 2', '16 -1 -1', '17 -1 -1', '18 -1 -1', '19 -1 -1', '20 -1 -1', '21 -1 -1'],
     1, ['0', '0', '0', '0', '2', '0 5866 7546 0 5', '2 5859 7457 0 5', '2', '1 6755 6018 0 11', '3 826 7013 0 17', '14', '0 4', '0 6', '0 7', '2 4', '2 6', '2 7', '1 11', '1 12', '1 5', '1 6', '3 4', '3 10', '3 7', '3 13', '2', '17 6516 7310 -527 118', '19 6298 8451 0 0', '34', '0 4 TL', '0 5 TL', '0 6 TR', '0 7 TL', '0 8 BR', '0 9 BL', '0 10 TL', '0 11 TR', '0 12 TR', '0 14 BL', '0 15 BR', '0 16 TL', '0 17 TR', '0 18 BL', '0 19 BR', '0 20 BL', '0 21 BR', '2 4 TL', '2 5 TL', '2 6 TR', '2 7 TL', '2 8 BR', '2 9 BL', '2 10 TL', '2 11 TR', '2 12 TR', '2 14 BL', '2 15 BR', '2 16 TL', '2 17 TR', '2 18 BL', '2 19 BR', '2 20 BL', '2 21 BR']),
    (['18', '4 0 0', '5 1 0', '6 0 1', '7 1 1', '8 0 2', '9 1 2', '10 2 0', '11 3 0', '12 2 1', '13 3 1', '14 2 2', '15 3 2', '16 -1 -1', '17 -1 -1', '18 -1 -1', '19 -1 -1', '20 -1 -1', '21 -1 -1'],
     1, ['0', '0', '0', '0', '2', '0 3776 3201 0 0', '2 4476 4459 0 0', '2', '1 9999 8802 0 30', '3 2557 5496 0 28', '11', '0 4', '2 4', '1 11', '1 4', '1 5', '1 6', '1 12', '3 5', '3 13', '3 7', '3 14', '2', '4 2257 4119 -171 104', '17 5022 3358 -240 484', '30', '0 4 BL', '0 5 BR', '0 6 BR', '0 7 BR', '0 11 BR', '0 12 BR', '0 13 BL', '0 14 BL', '0 15 BR', '0 16 BR', '0 17 BR', '0 18 TL', '0 19 BR', '0 20 BL', '0 21 BR', '2 4 TL', '2 5 TR', '2 6 BR', '2 7 BR', '2 11 TR', '2 12 BR', '2 13 BL', '2 14 BL', '2 15 BR', '2 16 BR', '2 17 TR', '2 18 TL', '2 19 BR', '2 20 BL', '2 21 BR']),
    (['16', '4 0 0', '5 1 0', '6 0 1', '7 1 1', '8 0 2', '9 1 2', '10 2 0', '11 3 0', '12 2 1', '13 3 1', '14 2 2', '15 3 2', '16 -1 -1', '17 -1 -1', '18 -1 -1', '19 -1 -1'],
     1, ['14', '0', '5', '4', '5', '11', '12', '13', '0', '2', '0 4788 4235 0 10', '2 4908 499 0 10', '2', '1 9916 7479 0 22', '3 2394 9384 0 22', '12', '1 4', '1 5', '1 10', '1 12', '1 13', '1 7', '3 4', '3 5', '3 12', '3 13', '3 11', '3 6', '0', '32', '0 4 TR', '0 5 BR', '0 6 BL', '0 7 BR', '0 8 BR', '0 9 BL', '0 10 TR', '0 11 BL', '0 12 BR', '0 13 BR', '0 14 BL', '0 15 BR', '0 16 BL', '0 17 BR', '0 18 BL', '0 19 BR', '2 4 BR', '2 5 BR', '2 6 BL', '2 7 BR', '2 8 BR', '2 9 BL', '2 10 BR', '2 11 BL', '2 12 BR', '2 13 BR', '2 14 BL', '2 15 BR', '2 16 BL', '2 17 BR', '2 18 BL', '2 19 BR']),
    (['16', '4 0 0', '5 1 0', '6 0 1', '7 1 1', '8 0 2', '9 1 2', '10 2 0', '11 3 0', '12 2 1', '13 3 1', '14 2 2', '15 3 2', '16 -1 -1', '17 -1 -1', '18 -1 -1', '19 -1 -1'],
     1, ['14', '0', '5', '4', '5', '11', '12', '13', '0', '2', '0 4977 3995 0 5', '2 5086 1072 0 5', '2', '1 9833 8073 0 23', '3 1805 9268 0 23', '12', '1 4', '1 5', '1 10', '1 12', '1 13', '1 7', '3 4', '3 5', '3 12', '3 13', '3 11', '3 6', '3', '4 6256 3276 -44 195', '18 3514 4235 533 -87', '19 5790 4329 -499 -205', '32', '0 4 TR', '0 5 BR', '0 6 BL', '0 7 BR', '0 8 BR', '0 9 BL', '0 10 TR', '0 11 BL', '0 12 BR', '0 13 BR', '0 14 BL', '0 15 BR', '0 16 BL', '0 17 BR', '0 18 BL', '0 19 BR', '2 4 BR', '2 5 BR', '2 6 BL', '2 7 BR', '2 8 BR', '2 9 BL', '2 10 BR', '2 11 BL', '2 12 BR', '2 13 BR', '2 14 BL', '2 15 BR', '2 16 BL', '2 17 BR', '2 18 BL', '2 19 BR']),
    (['14', '4 0 0', '5 1 0', '6 0 1', '7 1 1', '8 0 2', '9 1 2', '10 2 0', '11 3 0', '12 2 1', '13 3 1', '14 2 2', '15 3 2', '16 -1 -1', '17 -1 -1'],
     1, ['12', '66', '4', '10', '11', '6', '7', '10', '11', '12', '7', '8', '15', '6', '10', '13', '9', '14', '2', '0 4701 8225 0 4', '2 4701 8225 0 4', '2', '1 7377 5 0 10', '3 1825 5430 0 4', '6', '0 4', '0 12', '0 15', '2 4', '2 12', '2 15', '1', '17 4892 7482 -134 523', '24', '0 4 TR', '0 5 TL', '0 6 TR', '0 8 TR', '0 9 BL', '0 10 TL', '0 12 TR', '0 13 TL', '0 14 BL', '0 15 BR', '0 16 TR', '0 17 TR', '2 4 TR', '2 5 TL', '2 6 TR', '2 8 TR', '2 9 BL', '2 10 TL', '2 12 TR', '2 13 TL', '2 14 BL', '2 15 BR', '2 16 TR', '2 17 TR']),
    (['14', '4 0 0', '5 1 0', '6 0 1', '7 1 1', '8 0 2', '9 1 2', '10 2 0', '11 3 0', '12 2 1', '13 3 1', '14 2 2', '15 3 2', '16 -1 -1', '17 -1 -1'],
     1, ['12', '66', '4', '10', '11', '6', '7', '10', '11', '12', '7', '8', '15', '6', '10', '13', '9', '14', '2', '0 4120 8075 0 5', '2 4120 8075 0 5', '2', '1 7400 0 0 11', '3 1910 4836 0 5', '6', '0 4', '0 12', '0 15', '2 4', '2 12', '2 15', '1', '17 4758 8005 -537 59', '24', '0 4 TR', '0 5 TL', '0 6 TR', '0 8 TR', '0 9 BL', '0 10 TR', '0 12 TR', '0 13 TL', '0 14 BL', '0 15 BR', '0 16 TR', '0 17 TR', '2 4 TR', '2 5 TL', '2 6 TR', '2 8 TR', '2 9 BL', '2 10 TR', '2 12 TR', '2 13 TL', '2 14 BL', '2 15 BR', '2 16 TR', '2 17 TR']),
    (['18', '4 0 0', '5 1 0', '6 0 1', '7 1 1', '8 0 2', '9 1 2', '10 2 0', '11 3 0', '12 2 1', '13 3 1', '14 2 2', '15 3 2', '16 -1 -1', '17 -1 -1', '18 -1 -1', '19 -1 -1', '20 -1 -1', '21 -1 -1'],
     1, ['0', '0', '0', '0', '2', '0 4291 5000 0 0', '2 4687 5000 0 0', '2', '1 6976 6127 0 24', '3 2826 5788 0 24', '19', '0 11', '0 5', '0 4', '0 10', '0 12', '0 13', '2 5', '2 11', '2 4', '2 10', '2 12', '2 13', '1 10', '1 4', '1 13', '3 5', '3 11', '3 12', '3 7', '6', '4 5714 4807 393 -74', '5 3891 5000 -400 0', '10 6059 4728 392 -78', '11 5087 5000 400 0', '12 4879 6582 90 178', '13 5474 5924 259 305', '36', '0 4 TR', '0 5 TL', '0 6 BR', '0 7 BL', '0 8 BR', '0 9 BL', '0 10 TR', '0 11 TR', '0 12 BR', '0 13 BR', '0 14 BL', '0 15 BR', '0 16 BL', '0 17 BR', '0 18 BL', '0 19 BR', '0 20 BL', '0 21 BR', '2 4 TR', '2 5 TL', '2 6 BR', '2 7 BL', '2 8 BR', '2 9 BL', '2 10 TR', '2 11 TR', '2 12 BR', '2 13 BR', '2 14 BL', '2 15 BR', '2 16 BL', '2 17 BR', '2 18 BL', '2 19 BR', '2 20 BL', '2 21 BR']),
    (['18', '4 0 0', '5 1 0', '6 0 1', '7 1 1', '8 0 2', '9 1 2', '10 2 0', '11 3 0', '12 2 1', '13 3 1', '14 2 2', '15 3 2', '16 -1 -1', '17 -1 -1', '18 -1 -1', '19 -1 -1', '20 -1 -1', '21 -1 -1'],
     2, ['0', '0', '0', '0', '2', '0 1597 5156 0 5', '2 9454 4978 0 5', '2', '1 9529 6840 0 17', '3 1411 6254 0 22', '12', '0 4', '0 10', '0 7', '2 11', '1 5', '1 6', '1 11', '1 13', '1 9', '3 10', '3 12', '3 7', '0', '32', '0 6 BR', '0 7 BL', '0 8 BL', '0 9 BR', '0 10 TR', '0 11 TR', '0 12 BL', '0 13 BR', '0 14 BL', '0 15 BR', '0 16 BR', '0 17 BR', '0 18 BR', '0 19 BR', '0 20 BR', '0 21 BR', '2 6 BL', '2 7 BL', '2 8 BL', '2 9 BL', '2 10 TL', '2 11 TL', '2 12 BL', '2 13 BL', '2 14 BL', '2 15 BR', '2 16 BL', '2 17 BL', '2 18 BL', '2 19 BL', '2 20 BL', '2 21 BL', '0', '0', '0', '0', '2', '0 1259 5652 0 0', '2 9727 5078 0 0', '2', '1 9587 7437 0 18', '3 1263 6836 0 17', '14', '0 4', '0 10', '0 7', '0 12', '2 11', '1 5', '1 6', '1 11', '1 13', '1 9', '3 10', '3 12', '3 7', '3 8', '1', '12 459 6734 -397 -50', '30', '0 6 BR', '0 8 BL', '0 9 BR', '0 10 TR', '0 11 TR', '0 12 BL', '0 13 BR', '0 14 BL', '0 15 BR', '0 16 BR', '0 17 BR', '0 18 BR', '0 19 BR', '0 20 BR', '0 21 BR', '2 6 BL', '2 8 BL', '2 9 BL', '2 10 TL', '2 11 TL', '2 12 BL', '2 13 BL', '2 14 BL', '2 15 BL', '2 16 BL', '2 17 BL', '2 18 BL', '2 19 BL', '2 20 BL', '2 21 BL']),
    (['18', '4 0 0', '5 1 0', '6 0 1', '7 1 1', '8 0 2', '9 1 2', '10 2 0', '11 3 0', '12 2 1', '13 3 1', '14 2 2', '15 3 2', '16 -1 -1', '17 -1 -1', '18 -1 -1', '19 -1 -1', '20 -1 -1', '21 -1 -1'],
     1, ['0', '0', '0', '0', '2', '0 205 4106 0 4', '2 9387 5195 0 4', '2', '1 9399 7272 0 16', '3 682 7601 0 9', '19', '0 4', '0 10', '0 7', '0 12', '2 11', '2 6', '2 9', '2 13', '1 5', '1 6', '1 11', '1 13', '1 9', '1 15', '3 10', '3 4', '3 12', '3 8', '3 14', '0', '30', '0 4 TR', '0 6 BR', '0 8 BR', '0 9 BR', '0 10 BR', '0 11 TR', '0 13 BR', '0 14 BR', '0 15 BR', '0 16 BR', '0 17 BR', '0 18 BR', '0 19 BR', '0 20 BR', '0 21 BR', '2 4 TL', '2 6 BL', '2 8 BL', '2 9 BL', '2 10 TL', '2 11 TL', '2 13 BL', '2 14 BL', '2 15 BL', '2 16 BL', '2 17 BL', '2 18 BL', '2 19 BL', '2 20 BL', '2 21 BL']),
    (['14', '4 0 0', '5 1 0', '6 0 1', '7 1 1', '8 0 2', '9 1 2', '10 2 0', '11 3 0', '12 2 1', '13 3 1', '14 2 2', '15 3 2', '16 -1 -1', '17 -1 -1'],
     1, ['0', '0', '0', '0', '2', '0 2791 6666 0 0', '2 7495 6629 0 0', '2', '1 7633 6638 0 29', '3 4408 7383 0 18', '17', '0 5', '0 7', '0 12', '2 10', '2 6', '2 13', '2 15', '1 4', '1 6', '1 10', '1 11', '3 7', '3 10', '3 11', '3 12', '3 9', '3 14', '6', '7 2589 7336 -115 383', '12 1353 7255 -141 141', '6 8085 7441 196 349', '13 8472 7494 280 286', '15 6066 7676 200 0', '17 9163 5422 0 0', '28', '0 4 TR', '0 5 TL', '0 6 BR', '0 7 BL', '0 8 BR', '0 9 BR', '0 10 TR', '0 11 TR', '0 12 BL', '0 13 BR', '0 14 BR', '0 15 BR', '0 16 TL', '0 17 TR', '2 4 TR', '2 5 TL', '2 6 BR', '2 7 BL', '2 8 BL', '2 9 BL', '2 10 TL', '2 11 TL', '2 12 BL', '2 13 BR', '2 14 BL', '2 15 BL', '2 16 TL', '2 17 TR']),
    (['18', '4 0 0', '5 1 0', '6 0 1', '7 1 1', '8 0 2', '9 1 2', '10 2 0', '11 3 0', '12 2 1', '13 3 1', '14 2 2', '15 3 2', '16 -1 -1', '17 -1 -1', '18 -1 -1', '19 -1 -1', '20 -1 -1', '21 -1 -1'],
     2, ['18', '0', '5', '10', '11', '6', '8', '12', '0', '2', '1 3698 7489 0 5', '3 6776 7326 0 5', '2', '0 1867 2970 1 5', '2 7306 4734 0 1', '3', '1 13', '3 5', '3 13', '2', '6 7050 7500 338 214', '13 6050 7500 -389 93', '36', '1 4 TL', '1 5 TR', '1 6 BR', '1 7 TL', '1 8 BR', '1 9 BL', '1 10 TL', '1 11 TL', '1 12 TR', '1 13 BR', '1 14 BR', '1 15 BL', '1 16 BR', '1 17 TR', '1 18 TL', '1 19 BR', '1 20 TL', '1 21 TL', '3 4 TL', '3 5 TR', '3 6 BR', '3 7 TL', '3 8 BR', '3 9 BL', '3 10 TL', '3 11 TL', '3 12 BR', '3 13 BL', '3 14 BL', '3 15 BL', '3 16 BL', '3 17 TL', '3 18 TL', '3 19 BR', '3 20 BL', '3 21 TL',
         '18', '0', '5', '10', '11', '6', '8', '12', '0', '2', '1 3854 6910 0 6', '3 6340 7739 0 0', '2', '0 1867 2670 1 5', '2 7203 5325 0 2', '4', '1 13', '3 5', '3 13', '3 14', '6', '6 7388 7500 390 -89', '8 7292 8915 189 -66', '12 8108 7433 199 16', '13 5661 7500 -377 -133', '14 6735 9110 -189 66', '16 4610 9249 163 116', '36', '1 4 TL', '1 5 TR', '1 6 BR', '1 7 TL', '1 8 BR', '1 9 BL', '1 10 TL', '1 11 TL', '1 12 BR', '1 13 BR', '1 14 BR', '1 15 BL', '1 16 BR', '1 17 TR', '1 18 TL', '1 19 BR', '1 20 BL', '1 21 TL', '3 4 TL', '3 5 TR', '3 6 TR', '3 7 TL', '3 8 BR', '3 9 BL', '3 10 TL', '3 11 TL', '3 12 TR', '3 13 TL', '3 14 BR', '3 15 BL', '3 16 BL', '3 17 TL', '3 18 TL', '3 19 TR', '3 20 TL', '3 21 TL']),
    (['16', '4 0 0', '5 1 0', '6 0 1', '7 1 1', '8 0 2', '9 1 2', '10 2 0', '11 3 0', '12 2 1', '13 3 1', '14 2 2', '15 3 2', '16 -1 -1', '17 -1 -1', '18 -1 -1', '19 -1 -1'],
     9, ['0', '6', '0', '3', '10', '5', '11', '2', '0 4255 3427 0 29', '2 6244 3454 1 30', '2', '1 5047 2424 0 10', '3 3648 749 0 16', '3', '0 10', '0 11', '1 4', '2', '17 5719 4325 -247 -109', '19 5225 3590 -40 -267', '32', '0 4 BR', '0 5 BL', '0 6 BL', '0 7 BR', '0 8 BL', '0 9 BR', '0 10 BR', '0 11 BR', '0 12 BL', '0 13 BR', '0 14 BR', '0 15 BL', '0 16 BL', '0 17 BR', '0 18 BL', '0 19 BR', '2 4 BR', '2 5 BL', '2 6 BL', '2 7 BR', '2 8 BL', '2 9 BR', '2 10 BL', '2 11 BL', '2 12 BL', '2 13 BR', '2 14 BR', '2 15 BL', '2 16 BL', '2 17 BL', '2 18 BL', '2 19 BL',
         '0', '6', '0', '3', '10', '5', '11', '2', '0 4105 2846 0 30', '2 6244 3154 1 30', '2', '1 4714 2923 0 5', '3 3428 1307 0 11', '3', '0 10', '0 11', '1 4', '1', '19 5185 3323 -412 -350', '32', '0 4 BR', '0 5 BL', '0 6 BL', '0 7 BR', '0 8 BL', '0 9 BR', '0 10 BR', '0 11 BR', '0 12 BL', '0 13 BR', '0 14 BR', '0 15 BL', '0 16 BL', '0 17 BR', '0 18 BL', '0 19 BR', '2 4 BR', '2 5 BL', '2 6 BL', '2 7 BR', '2 8 BL', '2 9 BR', '2 10 BL', '2 11 BL', '2 12 BL', '2 13 BR', '2 14 BR', '2 15 BL', '2 16 BL', '2 17 BL', '2 18 BL', '2 19 BL',
         '0', '6', '0', '3', '10', '5', '11', '2', '0 3713 2391 0 30', '2 6244 2854 1 30', '2', '1 4257 2535 0 6', '3 3208 1865 0 6', '3', '0 10', '0 11', '1 4', '0', '32', '0 4 BR', '0 5 BL', '0 6 BL', '0 7 BR', '0 8 BL', '0 9 BR', '0 10 BR', '0 11 BR', '0 12 BL', '0 13 BR', '0 14 BR', '0 15 BL', '0 16 BR', '0 17 BR', '0 18 BR', '0 19 BR', '2 4 BR', '2 5 BL', '2 6 BL', '2 7 BR', '2 8 BL', '2 9 BR', '2 10 BL', '2 11 BL', '2 12 BL', '2 13 BR', '2 14 BR', '2 15 BL', '2 16 BL', '2 17 BL', '2 18 BL', '2 19 BL',
         '0', '6', '0', '3', '10', '5', '11', '2', '0 3338 1922 0 30', '2 6244 2554 1 30', '2', '1 3800 2147 0 7', '3 2988 2423 0 1', '3', '0 10', '0 11', '1 4', '0', '32', '0 4 BR', '0 5 BL', '0 6 BL', '0 7 BR', '0 8 BL', '0 9 BR', '0 10 BR', '0 11 BR', '0 12 BL', '0 13 BR', '0 14 BR', '0 15 BL', '0 16 BR', '0 17 BR', '0 18 BR', '0 19 BR', '2 4 BR', '2 5 BL', '2 6 BL', '2 7 BR', '2 8 BL', '2 9 BR', '2 10 BL', '2 11 BL', '2 12 BL', '2 13 BR', '2 14 BR', '2 15 BL', '2 16 BL', '2 17 BL', '2 18 BL', '2 19 BL',
         '0', '6', '0', '3', '10', '5', '11', '2', '0 3196 2505 0 30', '2 6244 2254 1 30', '2', '1 3343 1758 0 8', '3 2768 2981 0 2', '3', '0 10', '0 11', '1 4', '2', '16 3710 3196 -185 -197', '19 3950 2500 -540 4', '32', '0 4 BR', '0 5 BL', '0 6 BL', '0 7 BR', '0 8 BL', '0 9 BR', '0 10 BR', '0 11 BR', '0 12 BL', '0 13 BR', '0 14 BR', '0 15 BL', '0 16 BR', '0 17 BR', '0 18 BR', '0 19 TR', '2 4 BR', '2 5 BL', '2 6 BL', '2 7 BR', '2 8 BL', '2 9 BR', '2 10 BL', '2 11 BL', '2 12 BL', '2 13 BR', '2 14 BR', '2 15 BL', '2 16 BL', '2 17 BL', '2 18 BL', '2 19 BL',
         '0', '6', '0', '3', '10', '5', '11', '2', '0 2786 2066 0 30', '2 6244 1954 1 30', '2', '1 2963 1294 0 9', '3 2183 2847 0 3', '3', '0 10', '0 11', '1 4', '1', '19 3410 2504 -442 -310', '32', '0 4 BR', '0 5 BL', '0 6 BL', '0 7 BR', '0 8 BR', '0 9 BR', '0 10 BR', '0 11 BR', '0 12 BL', '0 13 BR', '0 14 BR', '0 15 BL', '0 16 BR', '0 17 BR', '0 18 BR', '0 19 BR', '2 4 BR', '2 5 BL', '2 6 BL', '2 7 BR', '2 8 BL', '2 9 BR', '2 10 BL', '2 11 BL', '2 12 BL', '2 13 BR', '2 14 BR', '2 15 BL', '2 16 BL', '2 17 BL', '2 18 BL', '2 19 BL',
         '0', '6', '0', '3', '10', '5', '11', '2', '0 2436 1579 0 30', '2 6244 1654 1 30', '2', '1 2770 1862 1 4', '3 2626 3252 0 4', '2', '0 10', '0 11', '1', '19 2968 2500 -221 155', '32', '0 4 BR', '0 5 BL', '0 6 BL', '0 7 BR', '0 8 BR', '0 9 BR', '0 10 BR', '0 11 BR', '0 12 BL', '0 13 BR', '0 14 BR', '0 15 BL', '0 16 BR', '0 17 BR', '0 18 BR', '0 19 BR', '2 4 BR', '2 5 BL', '2 6 BL', '2 7 BR', '2 8 BL', '2 9 BR', '2 10 BL', '2 11 BL', '2 12 BL', '2 13 BR', '2 14 BR', '2 15 BL', '2 16 BL', '2 17 BL', '2 18 BL', '2 19 BL',
         '0', '6', '0', '3', '10', '5', '11', '2', '0 2111 1074 0 30', '2 6244 1354 1 30', '2', '1 2770 1562 1 4', '3 2378 3798 0 5', '2', '0 10', '0 11', '0', '32', '0 4 BR', '0 5 BL', '0 6 BR', '0 7 BR', '0 8 BR', '0 9 BR', '0 10 BR', '0 11 BR', '0 12 BL', '0 13 BR', '0 14 BR', '0 15 BL', '0 16 BR', '0 17 BR', '0 18 BR', '0 19 BR', '2 4 BR', '2 5 BL', '2 6 BL', '2 7 BR', '2 8 BL', '2 9 BR', '2 10 BL', '2 11 BL', '2 12 BL', '2 13 BR', '2 14 BR', '2 15 BL', '2 16 BL', '2 17 BL', '2 18 BL', '2 19 BL',
         '0', '6', '0', '3', '10', '5', '11', '2', '0 2267 1653 0 30', '2 6244 1054 1 30', '2', '1 2770 1262 1 4', '3 2194 4369 0 6', '2', '0 10', '0 11', '0', '32', '0 4 BR', '0 5 BL', '0 6 BL', '0 7 BR', '0 8 BR', '0 9 BR', '0 10 BR', '0 11 BR', '0 12 BL', '0 13 BR', '0 14 BR', '0 15 BL', '0 16 BR', '0 17 BR', '0 18 BR', '0 19 BR', '2 4 BR', '2 5 BL', '2 6 BL', '2 7 BR', '2 8 BL', '2 9 BR', '2 10 BL', '2 11 BL', '2 12 BL', '2 13 BR', '2 14 BR', '2 15 BL', '2 16 BL', '2 17 BL', '2 18 BL', '2 19 BL']),
    (['14', '4 0 0', '5 1 0', '6 0 1', '7 1 1', '8 0 2', '9 1 2', '10 2 0', '11 3 0', '12 2 1', '13 3 1', '14 2 2', '15 3 2', '16 -1 -1', '17 -1 -1'],
     1, ['0', '0', '0', '0', '2', '0 2742 4035 0 27', '2 6995 4606 0 26', '2', '1 8860 5546 0 27', '3 1795 3768 0 21', '6', '0 11', '0 12', '2 5', '2 13', '3 4', '3 11', '1', '17 7569 5521 -143 -229', '26', '0 4 BR', '0 5 BR', '0 6 BL', '0 7 BR', '0 8 BL', '0 9 BR', '0 11 TL', '0 12 BL', '0 13 BR', '0 14 BR', '0 15 BR', '0 16 BL', '0 17 BR', '2 4 TL', '2 5 BL', '2 6 BL', '2 7 BR', '2 8 BL', '2 9 BR', '2 11 TL', '2 12 BL', '2 13 BR', '2 14 BL', '2 15 BR', '2 16 BL', '2 17 BR']),
    (['18', '4 0 0', '5 1 0', '6 0 1', '7 1 1', '8 0 2', '9 1 2', '10 2 0', '11 3 0', '12 2 1', '13 3 1', '14 2 2', '15 3 2', '16 -1 -1', '17 -1 -1', '18 -1 -1', '19 -1 -1', '20 -1 -1', '21 -1 -1'],
     1, ['38', '28', '8', '7', '5', '10', '4', '11', '12', '13', '15', '8', '5', '10', '7', '13', '4', '6', '12', '11', '2', '0 5396 2587 1 1', '2 3705 499 0 12', '2', '1 4719 3134 1 3', '3 7240 1843 0 0', '0', '2', '19 4865 3322 -146 137', '21 5294 2920 146 -137', '32', '0 5 BL', '0 7 BL', '0 8 BR', '0 9 BL', '0 10 BL', '0 11 BR', '0 12 BR', '0 13 BL', '0 14 BR', '0 15 BL', '0 16 BL', '0 17 BR', '0 18 BL', '0 19 BL', '0 20 BL', '0 21 BL', '2 5 BL', '2 7 BL', '2 8 BR', '2 9 BL', '2 10 BL', '2 11 BR', '2 12 BR', '2 13 BL', '2 14 BR', '2 15 BL', '2 16 BR', '2 17 BR', '2 18 BL', '2 19 BR', '2 20 BL', '2 21 BR']),
    (['16', '4 0 0', '5 1 0', '6 0 1', '7 1 1', '8 0 2', '9 1 2', '10 2 0', '11 3 0', '12 2 1', '13 3 1', '14 2 2', '15 3 2', '16 -1 -1', '17 -1 -1', '18 -1 -1', '19 -1 -1'],
     1, ['0', '0', '0', '0', '2', '0 4241 4301 0 13', '2 4000 4312 0 12', '2', '1 4230 7651 0 30', '3 409 3855 0 30', '24', '0 4', '0 13', '0 10', '0 6', '0 9', '0 12', '0 14', '0 15', '2 11', '2 5', '2 12', '2 7', '2 13', '1 5', '1 11', '1 12', '1 7', '1 8', '1 15', '1 14', '3 10', '3 4', '3 13', '3 6', '0', '28', '0 4 TR', '0 5 TR', '0 6 BL', '0 8 BR', '0 10 TR', '0 11 BL', '0 12 BR', '0 13 BR', '0 14 BL', '0 15 BR', '0 16 BL', '0 17 BR', '0 18 BL', '0 19 BL', '2 4 TR', '2 5 TR', '2 6 BL', '2 8 BR', '2 10 TR', '2 11 BL', '2 12 BR', '2 13 BR', '2 14 BL', '2 15 BR', '2 16 BL', '2 17 BR', '2 18 BL', '2 19 BL']),
    (['16', '4 0 0', '5 1 0', '6 0 1', '7 1 1', '8 0 2', '9 1 2', '10 2 0', '11 3 0', '12 2 1', '13 3 1', '14 2 2', '15 3 2', '16 -1 -1', '17 -1 -1', '18 -1 -1', '19 -1 -1'],
     1, ['34', '12', '8', '4', '13', '10', '6', '9', '12', '14', '15', '4', '10', '4', '13', '6', '2', '0 4241 499 0 20', '2 6545 5487 0 7', '2', '1 5480 3813 0 30', '3 409 0 0 30', '10', '2 11', '2 5', '2 7', '1 5', '1 11', '1 12', '1 7', '1 8', '1 15', '1 14', '0', '28', '0 4 BR', '0 5 BR', '0 6 BL', '0 8 BR', '0 10 BR', '0 11 BL', '0 12 BR', '0 13 BR', '0 14 BL', '0 15 BR', '0 16 BL', '0 17 BR', '0 18 BL', '0 19 BR', '2 4 TR', '2 5 TL', '2 6 BL', '2 8 BR', '2 10 TR', '2 11 TL', '2 12 BL', '2 13 BR', '2 14 BL', '2 15 BR', '2 16 BL', '2 17 BR', '2 18 BL', '2 19 TL']),
    (['16', '4 0 0', '5 1 0', '6 0 1', '7 1 1', '8 0 2', '9 1 2', '10 2 0', '11 3 0', '12 2 1', '13 3 1', '14 2 2', '15 3 2', '16 -1 -1', '17 -1 -1', '18 -1 -1', '19 -1 -1'],
      1, ['34', '12', '8', '4', '13', '10', '6', '9', '12', '14', '15', '4', '10', '4', '13', '6', '2', '0 4241 499 0 20', '2 6545 5487 0 7', '2', '1 5480 3813 0 30', '3 409 0 0 30', '10', '2 11', '2 5', '2 7', '1 5', '1 11', '1 12', '1 7', '1 8', '1 15', '1 14', '0', '28', '0 4 BR', '0 5 BR', '0 6 BL', '0 8 BR', '0 10 BR', '0 11 BL', '0 12 BR', '0 13 BR', '0 14 BL', '0 15 BR', '0 16 BL', '0 17 BR', '0 18 BL', '0 19 BR', '2 4 TR', '2 5 TL', '2 6 BL', '2 8 BR', '2 10 TR', '2 11 TL', '2 12 BL', '2 13 BR', '2 14 BL', '2 15 BR', '2 16 BL', '2 17 BR', '2 18 BL', '2 19 TL']),
    (['16', '4 0 0', '5 1 0', '6 0 1', '7 1 1', '8 0 2', '9 1 2', '10 2 0', '11 3 0', '12 2 1', '13 3 1', '14 2 2', '15 3 2', '16 -1 -1', '17 -1 -1', '18 -1 -1', '19 -1 -1'],
     1, ['55', '64', '11', '4', '13', '10', '6', '9', '12', '14', '15', '5', '11', '7', '11', '10', '4', '13', '6', '5', '11', '12', '7', '8', '15', '14', '2', '0 5163 2894 0 30', '2 5271 3362 0 30', '2', '1 5480 0 0 30', '3 409 0 0 30', '1', '0 8', '0', '28', '0 4 BR', '0 5 TL', '0 6 BL', '0 8 BL', '0 10 TR', '0 11 BL', '0 12 BL', '0 13 BR', '0 14 BR', '0 15 BL', '0 16 BL', '0 17 BR', '0 18 BL', '0 19 BR', '2 4 BR', '2 5 TL', '2 6 BL', '2 8 BL', '2 10 TR', '2 11 BL', '2 12 BL', '2 13 BR', '2 14 BR', '2 15 BL', '2 16 BL', '2 17 BR', '2 18 BL', '2 19 BR']),
    (['14', '4 0 0', '5 1 0', '6 0 1', '7 1 1', '8 0 2', '9 1 2', '10 2 0', '11 3 0', '12 2 1', '13 3 1', '14 2 2', '15 3 2', '16 -1 -1', '17 -1 -1'],
     3, ['0', '0', '0', '0', '2', '0 2251 4024 0 30', '2 6937 3975 0 30', '2', '1 7500 3700 0 20', '3 2500 3100 0 25', '6', '2 10', '1 4', '1 10', '1 7', '3 5', '3 11', '1', '10 7395 4207 357 181', '28', '0 4 TR', '0 5 TL', '0 6 BR', '0 7 BR', '0 8 BL', '0 9 BR', '0 10 BR', '0 11 TR', '0 12 BL', '0 13 BR', '0 14 BL', '0 15 BR', '0 16 BL', '0 17 BR', '2 4 TR', '2 5 TL', '2 6 BL', '2 7 BR', '2 8 BL', '2 9 BR', '2 10 BR', '2 11 BL', '2 12 BL', '2 13 BR', '2 14 BL', '2 15 BR', '2 16 BL', '2 17 BR',
         '0', '0', '0', '0', '2', '0 2112 4608 0 25', '2 7120 4546 0 30', '2', '1 7500 4300 0 15', '3 2500 3700 0 20', '10', '0 5', '0 6', '0 11', '2 10', '1 4', '1 10', '1 7', '3 5', '3 11', '3 6', '4', '5 582 3610 -161 118','6 2998 5579 270 295', '11 3835 4089 384 112', '10 7752 4388 378 132', '28', '0 4 TR', '0 5 TL', '0 6 BR','0 7 BR', '0 8 BL', '0 9 BR', '0 10 TR', '0 11 TR', '0 12 BL', '0 13 BR', '0 14 BL', '0 15 BR', '0 16 BL','0 17 BR', '2 4 TR', '2 5 TL', '2 6 BL', '2 7 BL', '2 8 BL', '2 9 BR', '2 10 TR', '2 11 TL', '2 12 BL','2 13 BR', '2 14 BL', '2 15 BR', '2 16 BL', '2 17 BR',
         '0', '0', '0', '0', '2', '0 1964 5189 0 20', '2 7314 5114 0 25', '2', '1 7500 4900 0 10', '3 2500 4300 0 15', '11', '0 5', '0 6', '0 11', '2 10', '2 7', '1 4', '1 10', '1 7', '3 5', '3 11', '3 6', '3', '6 3268 5874 135 148', '7 6955 5976 -154 369', '10 8130 4520 343 -207', '28', '0 4 TR', '0 5 TL', '0 6 BR', '0 7 BR', '0 8 BL', '0 9 BR', '0 10 TR', '0 11 TR', '0 12 BL', '0 13 BR', '0 14 BL', '0 15 BR', '0 16 BL', '0 17 BR', '2 4 TR', '2 5 TL', '2 6 BL', '2 7 BL', '2 8 BL', '2 9 BR', '2 10 TR', '2 11 TL', '2 12 BL', '2 13 BR', '2 14 BL', '2 15 BR', '2 16 BL', '2 17 BR']),
    (['18', '4 0 0', '5 1 0', '6 0 1', '7 1 1', '8 0 2', '9 1 2', '10 2 0', '11 3 0', '12 2 1', '13 3 1', '14 2 2', '15 3 2', '16 -1 -1', '17 -1 -1', '18 -1 -1', '19 -1 -1', '20 -1 -1', '21 -1 -1'],
     7, ['0', '24', '0', '5', '4', '10', '12', '14', '7', '2', '1 6055 6204 0 11', '3 3527 1965 1 16', '2', '0 574 480 0 8', '2 7914 3071 0 2', '8', '1 5', '1 11', '1 13', '1 12', '2 5', '2 11', '2 13', '2 6', '0', '34', '1 4 TL', '1 5 TL', '1 6 TR', '1 8 BL', '1 9 BR', '1 10 TL', '1 11 TR', '1 12 BL', '1 13 BL', '1 14 BL', '1 15 BR', '1 16 TL', '1 17 BR', '1 18 TL', '1 19 TR', '1 20 BL', '1 21 TR', '3 4 BR', '3 5 BR', '3 6 BR', '3 8 BL', '3 9 BR', '3 10 BR', '3 11 BR', '3 12 BR', '3 13 BR', '3 14 BR', '3 15 BR', '3 16 BL', '3 17 BR', '3 18 BL', '3 19 BR', '3 20 BR', '3 21 BR',
         '0', '24', '0', '5', '4', '10', '12', '14', '7', '2', '1 6422 6678 0 6', '3 3527 1665 1 16', '2', '0 759 1051 0 9', '2 7914 2471 0 3', '8', '1 5', '1 11', '1 13', '1 12', '2 5', '2 11', '2 13', '2 6', '4', '12 5789 7500 -244 317', '13 4751 7403 -199 -23', '17 7210 8322 -233 -487', '19 7791 5005 44 -266', '34', '1 4 TL', '1 5 TL', '1 6 TR', '1 8 BL', '1 9 BR', '1 10 TL', '1 11 TL', '1 12 BL', '1 13 BL', '1 14 BL', '1 15 BR', '1 16 TL', '1 17 BR', '1 18 TL', '1 19 TR', '1 20 BL', '1 21 TR', '3 4 BR', '3 5 BR', '3 6 BR', '3 8 BL', '3 9 BR', '3 10 BR', '3 11 BR', '3 12 BR', '3 13 BR', '3 14 BR', '3 15 BR', '3 16 BL', '3 17 BR', '3 18 BL', '3 19 BR', '3 20 BR', '3 21 BR',
         '0', '24', '0', '5', '4', '10', '12', '14', '7', '2', '1 6814 7132 0 7', '3 3527 1365 1 16', '2', '0 1244 1404 0 10', '2 7914 1871 0 4', '8', '1 5', '1 11', '1 13', '1 12', '2 5', '2 11', '2 13', '2 6', '1', '17 6977 7835 -122 -526', '34', '1 4 TL', '1 5 TL', '1 6 TR', '1 8 BL', '1 9 BR', '1 10 TL', '1 11 TL', '1 12 BL', '1 13 BL', '1 14 BL', '1 15 BR', '1 16 TL', '1 17 BR', '1 18 TL', '1 19 TR', '1 20 BL', '1 21 TR', '3 4 BR', '3 5 BR', '3 6 BR', '3 8 BL', '3 9 BR', '3 10 BR', '3 11 BR', '3 12 BR', '3 13 BR', '3 14 BR', '3 15 BR', '3 16 BL', '3 17 BR', '3 18 BL', '3 19 BR', '3 20 BR', '3 21 BR',
         '0', '24', '0', '5', '4', '10', '12', '14', '7', '2', '1 6678 6548 0 8', '3 3527 1065 1 16', '2', '0 1597 1889 0 11', '2 7914 1271 0 5', '8', '1 5', '1 11', '1 13', '1 12', '2 5', '2 11', '2 13', '2 6', '1', '17 6855 7309 -122 -526', '34', '1 4 TL', '1 5 TL', '1 6 TR', '1 8 BL', '1 9 BR', '1 10 TL', '1 11 TL', '1 12 BL', '1 13 BL', '1 14 BL', '1 15 BR', '1 16 TL', '1 17 BR', '1 18 TL', '1 19 TR', '1 20 BL', '1 21 TR', '3 4 BR', '3 5 BR', '3 6 BR', '3 8 BL', '3 9 BR', '3 10 BR', '3 11 BR', '3 12 BR', '3 13 BR', '3 14 BR', '3 15 BR', '3 16 BL', '3 17 BR', '3 18 BL', '3 19 BR', '3 20 BR', '3 21 BR',
         '0', '24', '0', '5', '4', '10', '12', '14', '7', '2', '1 6542 5964 0 9', '3 3527 765 1 16', '2', '0 1597 2489 0 12', '2 7914 671 0 6', '8', '1 5', '1 11', '1 13', '1 12', '2 5', '2 11', '2 13', '2 6', '1', '17 6733 6783 -61 -263', '34', '1 4 TL', '1 5 TL', '1 6 TR', '1 8 BL', '1 9 BR', '1 10 TL', '1 11 TL', '1 12 BL', '1 13 BL', '1 14 BL', '1 15 BR', '1 16 TL', '1 17 BR', '1 18 TL', '1 19 TR', '1 20 BL', '1 21 TR', '3 4 BR', '3 5 BR', '3 6 BR', '3 8 BL', '3 9 BR', '3 10 BR', '3 11 BR', '3 12 BR', '3 13 BR', '3 14 BR', '3 15 BR', '3 16 BL', '3 17 BR', '3 18 BL', '3 19 BR', '3 20 BR', '3 21 BR',
         '0', '52', '0', '9', '4', '10', '12', '14', '7', '5', '11', '13', '6', '2', '1 5821 5516 0 11', '3 3527 165 1 16', '2', '0 1950 3574 0 2', '2 7914 480 0 8', '4', '1 5', '1 11', '1 13', '1 12', '1', '17 6611 6257 -61 -263', '34', '1 4 TL', '1 5 TL', '1 6 TR', '1 8 BL', '1 9 BR', '1 10 TL', '1 11 TL', '1 12 BL', '1 13 BL', '1 14 BL', '1 15 BR', '1 16 TL', '1 17 BR', '1 18 TL', '1 19 TR', '1 20 BL', '1 21 TR', '3 4 BR', '3 5 BR', '3 6 BR', '3 8 BL', '3 9 BR', '3 10 BL', '3 11 BR', '3 12 BR', '3 13 BR', '3 14 BR', '3 15 BR', '3 16 BL', '3 17 BR', '3 18 BL', '3 19 BR', '3 20 BR', '3 21 BR',
         '0', '52', '0', '9', '4', '10', '12', '14', '7', '5', '11', '13', '6', '2', '1 5410 5953 0 12', '3 3527 0 0 16', '2', '0 2135 4145 0 3', '2 7914 1080 0 9', '4', '1 5', '1 11', '1 13', '1 12', '0', '34', '1 4 TL', '1 5 TL', '1 6 TR', '1 8 BL', '1 9 BR', '1 10 TL', '1 11 TR', '1 12 BL', '1 13 BL', '1 14 BL', '1 15 BR', '1 16 TL', '1 17 BR', '1 18 TL', '1 19 TR', '1 20 BL', '1 21 TR', '3 4 BR', '3 5 BR', '3 6 BR', '3 8 BL', '3 9 BR', '3 10 BL', '3 11 BR', '3 12 BR', '3 13 BR', '3 14 BR', '3 15 BR', '3 16 BL', '3 17 BR', '3 18 BL', '3 19 BR', '3 20 BR', '3 21 BR']),
    (['18', '4 0 0', '5 1 0', '6 0 1', '7 1 1', '8 0 2', '9 1 2', '10 2 0', '11 3 0', '12 2 1', '13 3 1', '14 2 2', '15 3 2', '16 -1 -1', '17 -1 -1', '18 -1 -1', '19 -1 -1', '20 -1 -1', '21 -1 -1'],
     1, ['0', '0', '0', '0', '2', '0 2419 7671 0 12', '2 8270 6828 0 18', '2', '1 9842 6425 0 30', '3 1019 5180 0 29', '8', '0 6', '0 10', '0 8', '2 7', '2 11', '1 5', '1 11', '3 10', '3', '16 2617 6705 -125 240', '17 7580 6399 229 142', '20 2695 8479 -51 -265', '32', '0 6 TR', '0 7 TR', '0 8 BL', '0 9 BR', '0 10 TL', '0 11 TR', '0 12 TL', '0 13 TR', '0 14 BR', '0 15 BR', '0 16 TR', '0 17 TR', '0 18 TL', '0 19 TR', '0 20 BR', '0 21 BR', '2 6 BL', '2 7 BL', '2 8 BL', '2 9 BL', '2 10 TL', '2 11 TL', '2 12 BL', '2 13 BR', '2 14 BL', '2 15 BL', '2 16 TL', '2 17 TL', '2 18 TL', '2 19 TR', '2 20 BL', '2 21 BL']),
    (['18', '4 0 0', '5 1 0', '6 0 1', '7 1 1', '8 0 2', '9 1 2', '10 2 0', '11 3 0', '12 2 1', '13 3 1', '14 2 2', '15 3 2', '16 -1 -1', '17 -1 -1', '18 -1 -1', '19 -1 -1', '20 -1 -1', '21 -1 -1'],
     1, ['0', '0', '0', '0', '2', '0 2758 7546 0 6', '2 8512 7199 0 0', '2', '1 9842 6425 0 30', '3 1019 5180 0 29', '10', '0 6', '0 10', '0 8', '2 7', '2 11', '2 9', '2 13', '1 5', '1 11', '3 10', '6', '9 7802 9011 162 118', '13 9778 7317 -29 399', '16 2443 6962 256 475', '17 7689 6853 498 209', '20 2629 8495 -83 -257', '21 7203 9009 0 0', '32', '0 6 TR', '0 7 TR', '0 8 BL', '0 9 BR', '0 10 TL', '0 11 TR', '0 12 TL', '0 13 TR', '0 14 BR', '0 15 BR', '0 16 TL', '0 17 TR', '0 18 TL', '0 19 TR', '0 20 BL', '0 21 BR', '2 6 BL', '2 7 BL', '2 8 BL', '2 9 BL', '2 10 TL', '2 11 TL', '2 12 BL', '2 13 BR', '2 14 BL', '2 15 BL', '2 16 TL', '2 17 TL', '2 18 TL', '2 19 TR', '2 20 BL', '2 21 BL']),
]


@pytest.mark.parametrize("init_inputs, nb_turns, turns_inputs", TEST_INPUTS)
def test_replay_turns(init_inputs: List[str], nb_turns: int, turns_inputs: List[str]):
    input_side_effect = [*init_inputs, *turns_inputs]
    with (patch(f"{BOT_PACKAGE}.game_loop.input", side_effect=input_side_effect)):
        running_side_effect = [*[True]*nb_turns, False]
        GameLoop.RUNNING = PropertyMock(side_effect=running_side_effect)
        GameLoop().start()


def init_game_loop(init_inputs: List[str]) -> GameLoop:
    with patch(f"{BOT_PACKAGE}.game_loop.input", side_effect=init_inputs):
        return GameLoop()


def start_game_loop(init_inputs: List[str], turns_inputs: List[str], running_side_effect: List[bool]):
    game_loop = init_game_loop(init_inputs)
    GameLoop.RUNNING = PropertyMock(side_effect=running_side_effect)
    with patch(f"{BOT_PACKAGE}.game_loop.input", side_effect=turns_inputs):
        game_loop.start()


def update_game_loop(init_inputs: List[str], turns_inputs: List[str]):
    game_loop = init_game_loop(init_inputs)
    with patch(f"{BOT_PACKAGE}.game_loop.input", side_effect=turns_inputs):
        game_loop.update_assets()


# @pytest.mark.skip
def test_perfs():
    R = 10
    N = 10
    print()
    init_perfs = []
    start_perfs = []
    update_perfs = []
    L = len(TEST_INPUTS)
    for i, test_inputs in enumerate(TEST_INPUTS):
        init_inputs, nb_turns, turns_inputs = test_inputs
        if nb_turns > 1:
            L -= 1
            continue
        with patch(f"{BOT_PACKAGE}.game_loop.print"):
            init_perf = sum(repeat(partial(init_game_loop, init_inputs), repeat=R, number=N))/(N*R)
            init_perfs.append(init_perf)

            running_side_effect = [*[True] * nb_turns, False]
            start_perf = sum(repeat(partial(start_game_loop, init_inputs, turns_inputs, running_side_effect), repeat=R, number=N))/(N*R)
            start_perfs.append(start_perf-init_perf)

            update_perf = sum(repeat(partial(update_game_loop, init_inputs, turns_inputs), repeat=R, number=N))/(N*R)
            update_perfs.append(update_perf-init_perf)

    print(f"init, start, update: {round(1000*sum(init_perfs)/L, 2)}ms, {round(1000*sum(start_perfs)/L, 2)}ms, {round(1000*sum(update_perfs)/L, 2)}ms (R = {R}, N = {N})")

    # last results : 0.47ms, 2.65ms, 0.83ms (R = 10, N = 10)
