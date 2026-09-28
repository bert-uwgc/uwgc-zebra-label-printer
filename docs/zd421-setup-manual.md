# Zebra ZD421 printer: setup and settings check

Use this guide on the Windows computer that will print to the ZD421. Ask ATS for help if the printer or a setting shown below is missing.

## 1. Contact ATS before connecting the printer

Contact the ATS team and ask them to push and install the Zebra ZD421 printer driver on your computer. **Do not connect the printer to the computer until ATS confirms that the driver is installed.**

## 2. Connect the printer

After ATS confirms installation, follow their connection instructions and connect the printer to the computer. Turn on the printer and wait for it to appear in Windows.

## 3. Check the printer settings

1. Open **Windows Settings > Bluetooth & devices > Printers & scanners**. Select the installed **ZDesigner ZD421** printer. Open **Printer properties** if you need to reach the window shown in the next image.

   ![ZD421 selected in Windows Printers and scanners](../images/Screenshot%202026-09-25%20142201.png)

2. In the ZD421 **Properties** window, select **Preferences** on the **General** tab. This opens the printer's **Printing Preferences**.

   ![ZD421 printer properties with Preferences button](../images/Screenshot%202026-09-25%20142250.png)

3. Open **Units** in the left menu. Set **Default measurement units** to **millimeter** so the size is displayed in metric units.

   ![ZD421 Printing Preferences Units set to millimeter](../images/Screenshot%202026-09-25%20142507.png)

4. Return to **Page Setup**. Use the following settings for the current badge labels:

   | Setting | Value |
   | --- | --- |
   | Stock > Select | Custom |
   | Width | 76 mm |
   | Height | 50 mm |
   | Media type | Labels with gaps |
   | Rotation | 0° - Portrait |
   | Mirror label / Inverse | Off / Off |

   The driver should show **Custom**, rather than use the printer's size setting. These values reflect the settings that produced better results with the current labels.

   ![ZD421 Page Setup with Custom 76 by 50 mm labels with gaps](../images/Screenshot%202026-09-28%20150729.png)

5. Open **Print Options** and check the current settings:

   | Setting | Value |
   | --- | --- |
   | Speed | 102 mm/s |
   | Darkness | 15 |
   | Printing mode | Thermal transfer |
   | Top offset | 2 mm |
   | Left offset | 1 mm |
   | Backfeed | Default |
   | Pause | No pause |
   | Control characters | Standard |
   | RTC refresh | Start print time |
   | Cancel all current and queued printing documents | Off |

   **Thermal transfer** is the default printing mode in this driver installation. The other values above are the current settings shown in the print options screenshot.

   ![ZD421 Print Options showing speed, darkness, thermal transfer, and offsets](../images/Screenshot%202026-09-28%20150751.png)

6. If you changed settings, select **Apply**, then **OK**. If the screen differs or a setting is unavailable, ask ATS to review the driver configuration.

## 4. Recalibrate if the printer cannot detect the labels

If the printer reports a media or label detection error, make sure labels are loaded correctly, the cover is closed, and the printer is on. Press and hold **Pause** and **Cancel** together for about **3 seconds**, then release. The printer should feed and measure a few labels. Wait for the **Status** light to return to solid green before printing again. Zebra specifies a two-second hold for this [SmartCal media calibration procedure](https://docs.zebra.com/us/en/printers/desktop/zd421-and-zd621-desktop-printers-user-guide/setup/running-a-smartcal-media-calibration.html). If the printer still cannot recognize the labels, ask ATS for help.

Zebra also directs Windows users to install the correct driver before connecting the printer to the computer: [ZD421 Windows driver setup](https://docs.zebra.com/us/en/printers/desktop/zd421-and-zd621-desktop-printers-user-guide/c-zd620-420-setup-for-windows/t-zd620-zd420-installing-the-windows-printer-drivers.html).
