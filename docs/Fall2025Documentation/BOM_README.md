# Bill of Materials (BOM) — MakiMate Robot

This document lists all parts required to build **one** MakiMate robot.

The BOM is organized by **Subsystem** to reflect the original color-coding used in Notion:

| Legend                 | Description                                      |
| ---------------------- | ------------------------------------------------ |
| Mechanical Engineering | Structural parts, fasteners, bearings, filament |
| Electrical Engineering | Power, wiring, connectors, drivers, audio, etc. |
| Computer Engineering   | Compute, control boards, digital interfaces     |

---

## Notes

- The following items are to be purchased to complete **1 MakiMate Robot**.
- The amount of **PLA filament** came out to be just over **2 kg per robot** — however, account for mistakes and printing errors as you progress through printing all the components.
- You might have a hard time finding the **OpenCM9.04** – this product was out of stock and on backorder from many websites as the team was building the prototype MakiMate for the **Fall 2025 semester**.

---

## Bill of Materials

| Subsystem             | Part                                         | Quantity & UOM | Link | Notes |
| --------------------- | -------------------------------------------- | -------------- | ---- | ----- |
| Computer Engineering  | Motor Communication Cable                    | 1 EA | [Buy here](https://www.robotis.us/robot-cable-x3p-180mm-convertible-10pcs/) |  |
| Computer Engineering  | OpenCM9.04                                   | 1 EA | [Buy here](https://en.robotis.com/shop_en/item.php?it_id=902-0084-040) |  |
| Computer Engineering  | 6” USB A to USB C Cable                      | 1 EA | [Buy here](https://www.amazon.com/Charging-Braided-iPhone-Samsung-Galaxy/dp/B0DPF8TFC9?crid=1HCR21BU09E3K&dib=eyJ2IjoiMSJ9.L1xbTl8k_tsrCHrJmjgtMu_0DXNF6Fdk-sWM_mUlWoHUuWp9QiV7C5W9oLim6Z3izEJvXUjpzXrcWCEZzSwcHDNvVsuFLqtmOE9e51b5i0Gr6ejw3M1J2JCkjdRumnbLzSCr4VdlmqWAStcY67m8zDH8nhRpozO8Ki82xrc8h91nqh3BRGwM7JsH6RSbjtwBWf_Jfl6eAu5ZlTrF-p6xHQ7uT8V-kHTTo8Umbj8mSmg.QdPsFlZ7hLDRV2sYtO-kUYXK4wi4j4E6oco74v9FcDM&dib_tag=se&keywords=6%2Binch%2Busb%2Bc%2Bcable&qid=1762090719&sprefix=6%2Binch%2Busb%2Bc%2Caps%2C177&sr=8-4&th=1) |  |
| Mechanical Engineering  | Brass Inserts                              | ~100 EA | [Buy here](https://www.amazon.com/dp/B00Y20YLKY) | Must have OD > 5.2 mm |
| Electrical            | DYNAMIXEL XL430-W250-T                       | 6 EA | [Buy here](https://www.robotis.us/dynamixel-xl430-w250-t/) |  |
| Electrical Engineering  | DC Power Jack Female Panel Mounting Connector Socket | 1 EA | [Buy here](https://www.amazon.com/gp/product/B01N8VV78D?ie=UTF8&psc=1) |  |
| Electrical Engineering  | Round Rocker Latching ON/Off               | 1 EA | [Buy here](https://www.amazon.com/Terminal-SPST-Rocker-Switch-Waterproof/dp/B09V1MSW15?dib=eyJ2IjoiMSJ9.Dre6pGVwhR2Os2pc5VjFUsbmKUgsG8F3rKNS_mJ2LsZiczeBS38pKkYmTYK1YS0eyuDWQcMvPIFcmmDiE0nlLyGdDOOmrHdtAnhqDGyqTfKE2yYjco8p82Vao8Xp0vkwcjzJRmXVKgZ3xcJ_HuJV526aGIcqf5r5woHJDtTycAKik2ykIeLFoKkTv1xlCy3fIUf6JYjePSkxHSBZpGpaB3BNaI-SCSKcS7ZsPJ91V-s._Og5Rxh4LdLuyNq9NkbhmfW-bVsKhIaQK039yddvSXQ&dib_tag=se&keywords=panel+mount+round+rocker+switch&qid=1763750250&sbo=RZvfv%2F%2FHxDF%2BO5021pAnSA%3D%3D&sr=8-4) |  |
| Computer Engineering  | Raspberry Pi Camera V3                       | 1 EA | [Buy here](https://www.amazon.com/Raspberry-Pi-Camera-Module/dp/B0BRY6MVXL?crid=2RQWH2A2MEUM2&dib=eyJ2IjoiMSJ9.xTArEZO8fJchsBqfEgy9_zKAq-0Ne3zQ3OXmQEYapCzYx3XolPejNcOdtLQO-4aN54Omylu5u0bbX4cJ3FA6oij6an5wJbSLNN1Ve4Av9ltmzoZG96xT7QS-ybOw4oSHPEwKDKMvdXPEevaYLF6ApIqVK32IFPkiFMmSTnr4bYjPQ0aY1aLtcZ99TUY7tXaNMkdjCDS9g_fxqp3M7t_dikS6QQ54JyWoct6WGvtzWg4.SuQiD6h50FIWxQR0Yi1_pQ6B3BoH4gKruVXlhVK3gfE&dib_tag=se&keywords=raspberry%2Bpi%2Bcamera%2Bv3&qid=1763750289&sprefix=raspberry%2Bpi%2Bcamera%2Bv3%2Caps%2C237&sr=8-2&th=1) | Ubuntu 24.04 on the Raspberry Pi 5 only works with **Raspberry Pi branded** camera modules |
| Computer Engineering  | Pi Camera Ribbon Cable                       | 1 EA | [Buy here](https://www.amazon.com/Pastall-Raspberry-15cm%C3%972pcs-30cm%C3%972pcs-50cm%C3%972pcs/dp/B089LM5D1T?crid=3O4NXAI8VPRPA&dib=eyJ2IjoiMSJ9.BwlH6lUOywrSefae0G3SRx5ODwEVtUedXWEuiGOq2se8secLjqKLsNJi2IvvVRJ88u2QgVKbF8RrgHL03mekKhEvgb_wVmQJTKxgYr4mLbvoZROknrNJ7a-Id0cey720nSj0Z5C0AaAJz_u7kAw_sBIq7IhNGN-jpODhW9RbR9iiV2McGUHrk9glC2X3WTfHxVyah9suj8s5GUM2ppxDUQjVnSSh7d8qo2XljxgRAJ9UVoda0VK3T1UlS_MP8iat6L8U5HVyFtV55RJ2hn61xaCaabRda7gHdIzd_fKPZR8.kCqz-kYC2RWdOQSSWRlxE34fvY3XV-1ZO8vb4cldHq4&dib_tag=se&keywords=raspberry+pi+5+camera+ribbon+cable&qid=1759261578&s=industrial&sprefix=raspberry+pi+5+camera+ribbon+cable%2Cindustrial%2C97&sr=1-1-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&psc=1) | Long cable required |
| Computer Engineering  | Raspberry Pi 5                               | 1 EA | [Buy here](https://www.amazon.com/Raspberry-Pi-SC1113-5-16GB/dp/B0DSPYPKRG?crid=XDKT2LXY6BHQ&dib=eyJ2IjoiMSJ9.FO5aBsV_9Rs5yd0tRacFoSdsxJWJ2D7OD2Lm_S-JfvZmdAyn6Xe0Pc8E5eVKbyVnVN6_HDP2PbugeRwpjTIvzGyRF5FXLZuxLYgiVig51sD4w6BSN3R1pSXWeYh66V1aRUO3AANne1TUaakMeBL_QKwGEZ2O8IeZDE6CzS8v6eL9FmAJHxna6u-LwjzQFVNyWsT0ja6Ojz5pGZ34Nb1z-bLhoiCzpiLwMZuGBcHZOds.YzdeGY8yPB7bbZkwCnRAmVraK7L9rXn6e62nr0cOYSE&dib_tag=se&keywords=raspberry+pi+5+16+gb&qid=1763750397&sprefix=raspberry+pi+5+16+gb%2Caps%2C228&sr=8-1) | 16 GB of RAM used |
| Computer Engineering  | Raspberry Pi 5 Heatsink                      | 1 EA | [Buy here](https://www.amazon.com/Raspberry-Pi-Active-Cooler/dp/B0CLXZBR5P?crid=34VSS79C6XYJL&dib=eyJ2IjoiMSJ9.x-XyN421aVJ3lmDqsvhzBBQO-oEu7cgjOKpJ3awZxgQnsk52AT09Uam3ekudYe08nNeDlh8-G6F2pSvKfTLliW4PnWbTrVFvr6InH7I_-ZYmDBg1eutVwhhG41jpZVDCJTiEVGu1543ecu-jjzp0mYG2RGadh4cx33GSK9ux4oEbO9PjDyku-qCkNdlcezXnGiFSjXb4O_PxbxkQGTyz6EPQi8Z_NPPSdxBTU0y0tzk.8rTEQsBoSCWVV3UmIhw3I2J3d81cLYQLvqSK3Av8950&dib_tag=se&keywords=raspberry+pi+5+heat+sink&qid=1759270520&sprefix=raspberry+pi+5+heat+sink%2Caps%2C177&sr=8-3) |  |
| Mechanical Engineering | Power Supply 12V 10A                         | 1 EA | [Buy here](https://www.amazon.com/gp/product/B07MXXXBV8?ie=UTF8&th=1) |  |
| Electrical Engineering | 22 AWG Solid Core Wire                       | Various Lengths | [Buy here](https://www.amazon.com/TUOFENG-Hookup-Wires-6-Different-Colored/dp/B07TX6BX47?dib=eyJ2IjoiMSJ9.0is0xfeGIMj9TEgcksIBUz8tIpSd2M7fSiyR7tzzhgXQzSj51rsSrAIjLUCBHkon8bG419_Se5XahdL7WTG4AB3ELfg4bgTNgTu-h0uiSDI8J6FmM00f9gsJcUt2oyhnymqDdfdkZZHR0mYx-jlTmPvRKv7Nk7Ge0PJk4_6seDnITpFZ7npWa6z4JkjTAAp-4T8U7cK56Xri8Wr7zZwxvYVDNeFNgvhqTPpGGP-7cxzZDiv8tA_7n4iaa2QO3glszDjb5dg6rX_-y6-LeRWHBiTJjpbIdnqNECHXhEThOuI.ZgqDZsMtHRjfbOHwEeR6bgIcBti59Z_0tGizic__SWg&dib_tag=se&keywords=22%2Bgauge%2Bwires&qid=1759263990&sr=8-5&th=1) |  |
| Electrical Engineering | DC-DC USB Buck Step Down Module              | 1 EA | [Buy here](https://www.amazon.com/dp/B01NALDSJ0) |  |
| Computer Engineering   | 90° USB cable panel mount                    | 1 EA | [Buy here](https://www.amazon.com/gp/product/B01J3N6HS8?ie=UTF8&th=1) |  |
| Computer Engineering   | Micro HDMI to HDMI panel mount               | 1 EA | [Buy here](https://www.amazon.com/dp/B0DHK3RN81) |  |
| Computer Engineering   | 3” 90° Micro USB Cable                       | 1 EA | [Buy here](https://www.amazon.com/gp/product/B01N337FQF?ie=UTF8&th=1) |  |
| Electrical Engineering | 4 pin header                                 | 1 EA | [Buy here](https://www.amazon.com/2-54mm-Single-Stackable-Shield-Arduino/dp/B084QFYMS4?crid=JBOCNUBRQ1NC&dib=eyJ2IjoiMSJ9.lkmKkIuqAnVPWJ48I0tLO3cWuqYk23LtOxX1340Wjw3glOg8_-wmQkIbVZ0Tyyjx88mID6LNuu7FYo6qewVBmrYukMrmSfJZEAwLsNbm7Cpn8u-etk1w8grf-FdzJtb6d-nzaAATBJd45wANB00JyZllEmc3Nq3xFUgEiNYD2T11ybMR3VfxmlNG1NYEsYe1B-8FBU-j7WOVPnbfGyxExW_w3IVEY2DLOfBHFIAdJ1Q.ezmJYaDpJM41nPNubJ3-QIo2ba-WLr8iZDoxXm0ue38&dib_tag=se&keywords=4+pin+header&qid=1763750693&sprefix=4+pin+headder%2Caps%2C284&sr=8-5) | Used for power delivery to OpenCM9.04 |
| Electrical Engineering | 2 Pin Connector Plug Wires                   | 3 EA | [Buy here](https://www.amazon.com/Letool-Electrical-Female-Connector-Cables/dp/B07FP2FCYC?crid=1IT8ZWOVXTW74&dib=eyJ2IjoiMSJ9.kNgR72EvkYb7iIzqcKSW-fVYBI2SoCo5z3an1EvFEE7qPabOvIkNZvJqvtfVNbLEYuhekvoW2NiUu5TJ0ZEYkJSEQEXxcuVtAb5U26Z0wgSvdnqNHDqEDjsHUdRWIqbyXVeu9hYpJQDOYQ8bADYyhnl4zCz-KvGtX4dC6XM8jPQhpw46w-RLzB9X5_gtLNz0NcLfyKEW6Zksr_-4oybusaXKMFsDINWvG-rk4X31xdI.64DB5BsDBtyOEAi08HKpjWB8dKcF7OvT77fKO84bVf8&dib_tag=se&keywords=2%2Bpin%2Bplug%2Bwire&qid=1763750755&sprefix=2%2Bpin%2Bplug%2Bwire%2Caps%2C210&sr=8-3&th=1) |  |
| Mechanical Engineering | M2 Bolts Assortment Kit                      | Various | [Buy here](https://www.amazon.com/Screws-Metric-Machine-Plated-Washers/dp/B0D3X4LJD2?crid=3GQUR06FM7LPZ&dib=eyJ2IjoiMSJ9.Gf5hYUNSMayZKQa4euVAl6_a56qwT76Rd23dPWjla7IYL8b90x-cwd78tm6c_S4fS8picd0L9uXI_nyjHyk7Hm457a2PjDUESxAz3blNdZk7zBUiwYwa7qwjZK_ijCzEY0IrVI6DzTJlSr3VGSNQGegXgg4jQerYR9hYWUONanP5V_UigGY1jOZ5eDVppOOmgMICvF86txZv6gcYXLjgji5YYffnb373FT78T6P_ZDc.s2gMLlBFq1YkcGi_lxysWjyMg5FOJETou4hTsFeInIc&dib_tag=se&keywords=m2%2Bassortment%2Bkit&qid=1763750806&sprefix=m2%2Bassort%2Caps%2C194&sr=8-5&th=1) |  |
| Mechanical Engineering | M3 Bolts Assortment Kit                      | Various | [Buy here](https://www.amazon.com/dp/B0CQJZCC9T?ref=cm_sw_r_cp_ud_dp_S8ZQ25DBF28JR6F3J3QT&social_share=cm_sw_r_cp_ud_dp_S8ZQ25DBF28JR6F3J3QT) |  |
| Mechanical Engineering | Ball Bearings                                | 1 | [Buy here](https://www.amazon.com/FR156ZZ-Miniature-Bearings-Shielded-Pre-Lubricated/dp/B0CRLFCNJ8?crid=Q6D3TRAXI34P&dib=eyJ2IjoiMSJ9.zU1KMEh-lNX1zJFs9IWsjS2bdft9P98OpTsN4XmYvSWIytsgCGZb5afnCy_IKztn7NU4eJ7UD07R-5c0NUOpw44jOYoqYu6AvcMn19eSeL1zYLcAJbdXKz-ruKmnqsqWjT3rnAWFo87K_B6_nVkLvbJXmV6u2_hlX7VLv2UlqjSVblOQKbN-7zOFEV5J1beb6B0qSqLs67bOiMil0Pbi7WwiZwVoo5iBrJo39rQ7fMM.gLxFtB2-0Wp5UF410Rkie-K9TI_6cXH1xAVQ8aDQeA8&dib_tag=se&keywords=3%2F16%2Bid%2B5%2F16%2Bod%2Bbearing&qid=1759265731&sprefix=3%2F16%2Bid%2B5%2F16%2Bod%2Bbearing%2Caps%2C121&sr=8-1-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&th=1) |  |
| Mechanical Engineering | Metal Dowel Pins                             | 1 | [Buy here](https://www.amazon.com/Hillman-Group-44242-1-Inch-12-Pack/dp/B00IZFXKRC?crid=26NXK0JN6O9W&dib=eyJ2IjoiMSJ9.c1Fl8c9ArYofwP2RzxvmG8vEEupXMvPD5W_5oN7iZ_aN1cSDxMPsC4NGLTneyErfRlM8Ki258maB-owcAzxiUV28SLX0P_-YmOjrWe1_mIqAlfPABu1q3TNoqQh-ESKeWg_a1tSdky6Zv3gbRjUYyxc6qBlwTy33TCFoLHr5tG7z0GSeS2iN5Xn63AhugcfqcY0WkBPPXEqLXqyMptnAqlp3Kcl_LcD6CfOgdZAZgvw.zr7QtfK4obGgeusRf5triroUlINmjD56TSENikBrolk&dib_tag=se&keywords=3%2F16+x+1+inch+pin&qid=1759265808&sprefix=3%2F16+x+1+inch+pin%2Caps%2C113&sr=8-4) |  |
| Mechanical Engineering | PLA Filament                                 | ~2.2 kg |  | Assume extra for failed/experimental prints |
| Electrical Engineering | Aux Cable with Screw Terminals               | 1 EA | [Buy here](https://www.amazon.com/dp/B0F31SS3NK?ref=ppx_yo2ov_dt_b_fed_asin_title&th=1) |  |
| Electrical Engineering | 90° USB Cable Extension                      | 1 EA | [Buy here](https://www.amazon.com/dp/B0986QR9H6?ref=ppx_yo2ov_dt_b_fed_asin_title) |  |
| Electrical Engineering | USB to Aux Out w/ DAC                        | 1 EA | [Buy here](https://www.amazon.com/dp/B07WXQQ3ML?ref=ppx_yo2ov_dt_b_fed_asin_title) |  |
| Electrical Engineering | Speaker Stereo                               | 1 EA | [Buy here](https://www.amazon.com/dp/B081169PC5?ref=ppx_yo2ov_dt_b_fed_asin_title) |  |
| Electrical Engineering | 5V Audio Amplifier                           | 1 EA | [Buy here](https://www.amazon.com/dp/B00LODGV64?ref=ppx_yo2ov_dt_b_fed_asin_title) |  |

---

## 🧭 Navigation

🔙 Back to Main Documentation  
➡️ [`../../README.md`](Overall_README.md)
