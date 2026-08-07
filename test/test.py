# SPDX-FileCopyrightText: 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.types import LogicArray
from cocotb.binary import BinaryValue
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles
from cocotb.triggers import RisingEdge, FallingEdge, Timer, ClockCycles

# Helper Functions
# ----------------
#def transmit_image(dut, input_image):
#    dut._log.info("Transmitting Image...")
#    dut.ui_in.value = 0 # Negative Edge (start transmission)
#    await ClockCycles(dut.clk, 1)
#    for i in range(0, 28):
#        dut.ui_in.value = 128 #[1,0,0,0,0,0,0,0]
#        await ClockCycles(dut.clk, 1)
#    dut._log.info("Transmitting Image...Done")

# Seven Segments Lookup Table
# ---------------------------
# Integer representation of the 7 segments for digits 0-9
segments = [ 63, 6, 91, 79, 102, 109, 125, 7, 127, 111 ]

####################################################################
#                                                                  #
#                      7 Segment Output Tests                      #
#                                                                  #
####################################################################

@cocotb.test()
async def test_blank_image_with_0_checksum(dut):
    # Test 1: Blank Image
    # Author: estods3
    # Input: Blank (all 0s) 14x14 image.
    # Expected Result: BCD = 0, Seven Segment = 63
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000")]

    classification_result = 0

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter "READ" Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info("Transmitting Image...")
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info("Transmitting Image...Done")

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    dut._log.info("Evaluating...")
    print(dut.uo_out.value)
    print(dut.uio_out.value)
    print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if("1.8.1" in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info("Evaluating...Done")

@cocotb.test()
async def test_blank_image_with_1_checksum(dut):
    # Test 2: Blank Image with 1 checksum
    # Author: estods3
    # Input: Blank (all 0s) 14x14 image with a '1' in LSB
    # Expected Result: BCD = 1, Seven Segment = 6
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000001")]

    classification_result = 1

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter "READ" Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info("Transmitting Image...")
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info("Transmitting Image...Done")

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    dut._log.info("Evaluating...")
    print(dut.uo_out.value)
    print(dut.uio_out.value)
    print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if("1.8.1" in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info("Evaluating...Done")

@cocotb.test()
async def test_blank_image_with_2_checksum(dut):
    # Test 3: Blank Image with 2 checksum
    # Author: estods3
    # Input: Blank (all 0s) 14x14 image with a 2 checksum
    # Expected Result: BCD = 2, Seven Segment = 91
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000010")]

    classification_result = 2

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter "READ" Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info("Transmitting Image...")
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        #print(dut.ui_in.value)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
        #print(dut.ui_in.value)
    dut._log.info("Transmitting Image...Done")

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    dut._log.info("Evaluating...")
    print(dut.uo_out.value)
    print(dut.uio_out.value)
    print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if("1.8.1" in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info("Evaluating...Done")

@cocotb.test()
async def test_blank_image_with_3_checksum(dut):
    # Test 4: Blank Image with 3 checksum
    # Author: estods3
    # Input: Blank (all 0s) 14x14 image with a 3 checksum
    # Expected Result: BCD = 3, Seven Segment = 79
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000011")]

    classification_result = 3

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter "READ" Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info("Transmitting Image...")
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info("Transmitting Image...Done")

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    dut._log.info("Evaluating...")
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if("1.8.1" in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info("Evaluating...Done")

@cocotb.test()
async def test_blank_image_with_4_checksum(dut):
    # Test 5: Blank Image with 4 checksum
    # Author: estods3
    # Input: Blank (all 0s) 14x14 image with a 4 checksum
    # Expected Result: BCD = 4, Seven Segment = 102
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000100")]

    classification_result = 4

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter "READ" Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info("Transmitting Image...")
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info("Transmitting Image...Done")

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    dut._log.info("Evaluating...")
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if("1.8.1" in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info("Evaluating...Done")

@cocotb.test()
async def test_blank_image_with_5_checksum(dut):
    # Test 6: Blank Image with 5 checksum
    # Author: estods3
    # Input: Blank (all 0s) 14x14 image with a 5 checksum
    # Expected Result: BCD = 5, Seven Segment = 109
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000101")]

    classification_result = 5

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter "READ" Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info("Transmitting Image...")
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info("Transmitting Image...Done")

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    dut._log.info("Evaluating...")
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if("1.8.1" in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info("Evaluating...Done")

@cocotb.test()
async def test_blank_image_with_6_checksum(dut):
    # Test 7: Blank Image with 6 checksum
    # Author: estods3
    # Input: Blank (all 0s) 14x14 image with a 6 checksum
    # Expected Result: BCD = 6, Seven Segment = 125
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000110")]

    classification_result = 6

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter "READ" Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info("Transmitting Image...")
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info("Transmitting Image...Done")

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    dut._log.info("Evaluating...")
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if("1.8.1" in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info("Evaluating...Done")

@cocotb.test()
async def test_blank_image_with_7_checksum(dut):
    # Test 8: Blank Image with 7 checksum
    # Author: estods3
    # Input: Blank (all 0s) 14x14 image with a 7 checksum
    # Expected Result: BCD = 7, Seven Segment = 7
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000111")]

    classification_result = 7

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter "READ" Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info("Transmitting Image...")
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info("Transmitting Image...Done")

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    dut._log.info("Evaluating...")
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if("1.8.1" in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info("Evaluating...Done")

@cocotb.test()
async def test_blank_image_with_8_checksum(dut):
    # Test 9: Blank Image with 8 checksum
    # Author: estods3
    # Input: Blank (all 0s) 14x14 image with a 8 checksum
    # Expected Result: BCD = 8, Seven Segment = 127
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000001000")]

    classification_result = 8

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter "READ" Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info("Transmitting Image...")
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info("Transmitting Image...Done")

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    dut._log.info("Evaluating...")
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if("1.8.1" in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info("Evaluating...Done")

@cocotb.test()
async def test_blank_image_with_9_checksum(dut):
    # Test 10: Blank Image with 9 checksum
    # Author: estods3
    # Input: Blank (all 0s) 14x14 image with a 9 checksum
    # Expected Result: BCD = 9, Seven Segment = 111
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000001001")]

    classification_result = 9

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter "READ" Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info("Transmitting Image...")
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info("Transmitting Image...Done")

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    dut._log.info("Evaluating...")
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if("1.8.1" in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info("Evaluating...Done")

####################################################################
#                                                                  #
#                        SIMPLE DIGIT TESTS                        #
#                                                                  #
####################################################################

@cocotb.test()
async def test_example_output_1(dut):
    # Test 11: Example '1'
    # Author: estods3
    # Input: 14x14 image of a '1'
    # Expected Result: BCD = 1, Seven Segment = 6
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000001000000"), \
                   LogicArray("00000001000000"), \
                   LogicArray("00000001000000"), \
                   LogicArray("00000001000000"), \
                   LogicArray("00000001000000"), \
                   LogicArray("00000001000000"), \
                   LogicArray("00000001000000"), \
                   LogicArray("00000001000000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000")]

    classification_result = 1

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter "READ" Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info("Transmitting Image...")
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info("Transmitting Image...Done")

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    dut._log.info("Evaluating...")
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if("1.8.1" in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info("Evaluating...Done")

####################################################################
#                                                                  #
#                   AUTOGENERATED MNIST TEST CASES                 #
#                                                                  #
####################################################################

@cocotb.test()
async def test_mnist_batch1_sample21(dut):
    # THIS TEST WAS AUTOGENERATED USING data_preprocessor.py
    # Test: Batch=1, Sample=21
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 4
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000011000"), \
                   LogicArray("00011000111000"), \
                   LogicArray("00011100111000"), \
                   LogicArray("00011101111000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00000001111000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 4

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    print(dut.uo_out.value)
    print(dut.uio_out.value)
    print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')

@cocotb.test()
async def test_mnist_batch0_sample11(dut):
    # THIS TEST WAS AUTOGENERATED USING data_preprocessor.py
    # Test: Batch=0, Sample=11
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 6
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00001100000000"), \
                   LogicArray("00001100011000"), \
                   LogicArray("00011101111100"), \
                   LogicArray("00011011111100"), \
                   LogicArray("00011111001100"), \
                   LogicArray("00011111001100"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 6

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch1_sample23(dut):
    # THIS TEST WAS AUTOGENERATED USING data_preprocessor.py
    # Test: Batch=1, Sample=23
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 3
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00011111000000"), \
                   LogicArray("00111111000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00011001111100"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000001111000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 3

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch1_sample13(dut):
    # THIS TEST WAS AUTOGENERATED USING data_preprocessor.py
    # Test: Batch=1, Sample=13
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 2
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00111000110000"), \
                   LogicArray("00110000110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000111111110"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 2

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch1_sample63(dut):
    # THIS TEST WAS AUTOGENERATED USING data_preprocessor.py
    # Test: Batch=1, Sample=63
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 5
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000011100"), \
                   LogicArray("00000011111100"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00011111000000"), \
                   LogicArray("00011100000000"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00001001110000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 5

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch1_sample10(dut):
    # THIS TEST WAS AUTOGENERATED USING data_preprocessor.py
    # Test: Batch=1, Sample=10
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 1
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 1

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch0_sample5(dut):
    # THIS TEST WAS AUTOGENERATED USING data_preprocessor.py
    # Test: Batch=0, Sample=5
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 1
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000010000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 1

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch1_sample37(dut):
    # THIS TEST WAS AUTOGENERATED USING data_preprocessor.py
    # Test: Batch=1, Sample=37
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 0
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00001111111100"), \
                   LogicArray("00001110001100"), \
                   LogicArray("00011100001100"), \
                   LogicArray("00011000001100"), \
                   LogicArray("00011000001100"), \
                   LogicArray("00011000011100"), \
                   LogicArray("00001100111000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 0

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch0_sample12(dut):
    # THIS TEST WAS AUTOGENERATED USING data_preprocessor.py
    # Test: Batch=0, Sample=12
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 9
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00001110111000"), \
                   LogicArray("00001100110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
    ]

    classification_result = 9

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch0_sample18(dut):
    # THIS TEST WAS AUTOGENERATED USING data_preprocessor.py
    # Test: Batch=0, Sample=18
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 3
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00011100000000"), \
                   LogicArray("00111111000000"), \
                   LogicArray("00110111100000"), \
                   LogicArray("00111111100000"), \
                   LogicArray("00111111111000"), \
                   LogicArray("00001111111100"), \
                   LogicArray("00001100011110"), \
                   LogicArray("00001110001110"), \
                   LogicArray("00000111111110"), \
                   LogicArray("00000011111100"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 3

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')

@cocotb.test()
async def test_mnist_batch1_sample30_output1(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=1, Sample=30
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 1
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 1

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch0_sample32_output3(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=0, Sample=32
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 3
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00011011100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000000011000"), \
                   LogicArray("00000001111000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 3

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch1_sample5_output0(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=1, Sample=5
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 0
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00001111111100"), \
                   LogicArray("00011100000110"), \
                   LogicArray("00111000000110"), \
                   LogicArray("00110000000110"), \
                   LogicArray("00110000001110"), \
                   LogicArray("00111111111100"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 0

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch1_sample38_output5(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=1, Sample=38
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 5
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00001111111110"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00111110000000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00011111000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 5

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch0_sample58_output9(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=0, Sample=58
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 9
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00011110111000"), \
                   LogicArray("00011000111000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000001000000"), \
    ]

    classification_result = 9

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch0_sample34_output7(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=0, Sample=34
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 7
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00001111111100"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00011100000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 7

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch0_sample35_output2(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=0, Sample=35
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 2
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00001111111100"), \
                   LogicArray("00011100001100"), \
                   LogicArray("00011000011100"), \
                   LogicArray("00000000011000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00011111100100"), \
                   LogicArray("00111111111100"), \
                   LogicArray("00111100111000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 2

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch0_sample23_output5(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=0, Sample=23
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 5
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000111100"), \
                   LogicArray("00000111111110"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00011111000000"), \
                   LogicArray("00001100000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 5

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch1_sample52_output4(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=1, Sample=52
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 4
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000110010000"), \
                   LogicArray("00000100110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000000100000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 4

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch1_sample60_output7(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=1, Sample=60
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 7
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("01100000000000"), \
                   LogicArray("01100000011100"), \
                   LogicArray("01111111111100"), \
                   LogicArray("00111111111000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 7

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch58_sample49_output1(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=58, Sample=49
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 1
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000010000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000001000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 1

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch105_sample5_output8(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=105, Sample=5
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 8
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000011111110"), \
                   LogicArray("00000111111110"), \
                   LogicArray("00000110111100"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00011111000000"), \
                   LogicArray("00011110000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 8

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch140_sample36_output6(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=140, Sample=36
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 6
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00001111111100"), \
                   LogicArray("00011111111110"), \
                   LogicArray("00011111001110"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 6

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch6_sample39_output2(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=6, Sample=39
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 2
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00011111000000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00000110011000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 2

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch138_sample48_output2(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=138, Sample=48
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 2
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000011111000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000110011000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00111111100000"), \
                   LogicArray("00111111110000"), \
                   LogicArray("00111111111000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 2

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch65_sample33_output6(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=65, Sample=33
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 6
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000010000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000110011100"), \
                   LogicArray("00001110111100"), \
                   LogicArray("00001101111000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 6

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch108_sample59_output0(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=108, Sample=59
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 0
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001110111000"), \
                   LogicArray("00001110011000"), \
                   LogicArray("00001110011000"), \
                   LogicArray("00001110011000"), \
                   LogicArray("00001100111000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 0

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch45_sample43_output9(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=45, Sample=43
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 9
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00001101110000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000001000000"), \
    ]

    classification_result = 9

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch123_sample5_output7(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=123, Sample=5
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 7
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111111100"), \
                   LogicArray("00001111111100"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001101110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00011110000000"), \
                   LogicArray("00011100000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 7

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch123_sample58_output2(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=123, Sample=58
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 2
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00111111111100"), \
                   LogicArray("00111111111100"), \
                   LogicArray("00011100111100"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 2

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch26_sample9_output1(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=26, Sample=9
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 1
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000001000000"), \
                   LogicArray("00000001000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 1

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch29_sample29_output1(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=29, Sample=29
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 1
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000001100"), \
                   LogicArray("00000000011100"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 1

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch39_sample45_output1(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=39, Sample=45
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 1
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 1

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch91_sample30_output7(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=91, Sample=30
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 7
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00011100111000"), \
                   LogicArray("00011100110000"), \
                   LogicArray("00111000110000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 7

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch25_sample34_output4(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=25, Sample=34
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 4
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000010011000"), \
                   LogicArray("00000110111000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 4

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch18_sample49_output1(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=18, Sample=49
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 1
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 1

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch39_sample33_output1(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=39, Sample=33
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 1
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 1

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch8_sample14_output3(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=8, Sample=14
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 3
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000000011000"), \
                   LogicArray("00000000011000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 3

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch23_sample12_output1(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=23, Sample=12
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 1
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 1

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch128_sample3_output0(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=128, Sample=3
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 0
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00001111011100"), \
                   LogicArray("00011110001100"), \
                   LogicArray("00111100001110"), \
                   LogicArray("00111000000110"), \
                   LogicArray("00111000001110"), \
                   LogicArray("00111000111100"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 0

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch34_sample27_output8(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=34, Sample=27
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 8
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000110110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 8

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch114_sample50_output6(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=114, Sample=50
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 6
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001111111100"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 6

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch125_sample30_output7(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=125, Sample=30
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 7
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00000000111100"), \
                   LogicArray("00000001111000"), \
                   LogicArray("00000011111000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00011110000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 7

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch107_sample38_output5(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=107, Sample=38
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 5
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00011000011000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 5

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch23_sample34_output2(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=23, Sample=34
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 2
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011111000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00011110011000"), \
                   LogicArray("00001000111000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00011100000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 2

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch90_sample8_output6(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=90, Sample=8
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 6
    # --------------------------------------------
    input_image = [LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00011110000000"), \
                   LogicArray("00011100011100"), \
                   LogicArray("00011001111110"), \
                   LogicArray("00011111111110"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 6

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...123')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch138_sample44_output3(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=138, Sample=44
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 3
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000001111000"), \
                   LogicArray("00000001111000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00111001110000"), \
                   LogicArray("00111111110000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 3

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch131_sample26_output8(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=131, Sample=26
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 8
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00001110110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 8

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch26_sample49_output0(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=26, Sample=49
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 0
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00001110111000"), \
                   LogicArray("00011100011000"), \
                   LogicArray("00011000011000"), \
                   LogicArray("00011000011100"), \
                   LogicArray("00011000011100"), \
                   LogicArray("00011000011000"), \
                   LogicArray("00011000111000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 0

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch6_sample38_output9(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=6, Sample=38
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 9
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00011100110000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 9

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch8_sample40_output0(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=8, Sample=40
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 0
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00011101111000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 0

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch148_sample2_output3(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=148, Sample=2
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 3
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00011001110000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00011111000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 3

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch82_sample53_output0(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=82, Sample=53
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 0
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00001110111000"), \
                   LogicArray("00001110011000"), \
                   LogicArray("00001110111000"), \
                   LogicArray("00001110111000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 0

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch83_sample9_output0(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=83, Sample=9
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 0
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001110111100"), \
                   LogicArray("00011110011100"), \
                   LogicArray("00011100011000"), \
                   LogicArray("00011100111000"), \
                   LogicArray("00011100111000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 0

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch10_sample6_output2(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=10, Sample=6
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 2
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000111111111"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00001000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 2

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch127_sample48_output4(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=127, Sample=48
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 4
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000001100"), \
                   LogicArray("00000100011100"), \
                   LogicArray("00001110011000"), \
                   LogicArray("00001100111000"), \
                   LogicArray("00011100110000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000010000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 4

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch5_sample39_output9(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=5, Sample=39
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 9
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00011101111000"), \
                   LogicArray("00011101110000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 9

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch22_sample29_output4(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=22, Sample=29
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 4
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00011000000000"), \
                   LogicArray("00011001100000"), \
                   LogicArray("00001101100000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000000100000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 4

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch102_sample63_output6(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=102, Sample=63
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 6
    # --------------------------------------------
    input_image = [LogicArray("00000110000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00001100000000"), \
                   LogicArray("00011100000000"), \
                   LogicArray("00011000000000"), \
                   LogicArray("00011000000000"), \
                   LogicArray("00011011111000"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00001110011100"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 6

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch148_sample58_output9(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=148, Sample=58
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 9
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011111000"), \
                   LogicArray("00000011111000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 9

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch0_sample63_output3(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=0, Sample=63
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 3
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000010000000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00011011100000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00011110000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 3

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch67_sample18_output3(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=67, Sample=18
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 3
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00001100000000"), \
                   LogicArray("00001111111100"), \
                   LogicArray("00000111111100"), \
                   LogicArray("00000001111000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 3

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch53_sample60_output1(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=53, Sample=60
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 1
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000100000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 1

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch62_sample23_output6(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=62, Sample=23
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 6
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00001100110000"), \
                   LogicArray("00001101110000"), \
                   LogicArray("00001101111000"), \
                   LogicArray("00001101111000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 6

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch109_sample40_output8(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=109, Sample=40
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 8
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111010000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 8

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch136_sample20_output1(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=136, Sample=20
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 1
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 1

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch83_sample34_output3(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=83, Sample=34
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 3
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00011000110000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 3

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch155_sample6_output8(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=155, Sample=6
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 8
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011000110"), \
                   LogicArray("00000111001110"), \
                   LogicArray("00000110011100"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00111111000000"), \
                   LogicArray("00111100000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 8

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch31_sample62_output4(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=31, Sample=62
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 4
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000011000"), \
                   LogicArray("00001100110000"), \
                   LogicArray("00001100110000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 4

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch25_sample15_output3(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=25, Sample=15
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 3
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00111111000000"), \
                   LogicArray("00110111100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000000001100"), \
                   LogicArray("00000000001100"), \
                   LogicArray("00111001111100"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 3

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch33_sample3_output7(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=33, Sample=3
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 7
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00011100011100"), \
                   LogicArray("00011100011100"), \
                   LogicArray("00011100111000"), \
                   LogicArray("00011001111000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 7

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch66_sample28_output6(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=66, Sample=28
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 6
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 6

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch40_sample39_output1(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=40, Sample=39
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 1
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 1

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch117_sample25_output7(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=117, Sample=25
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 7
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000011100"), \
                   LogicArray("00001111111100"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00111110111000"), \
                   LogicArray("00111001110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000110000000"), \
    ]

    classification_result = 7

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch77_sample18_output4(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=77, Sample=18
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 4
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000001000"), \
                   LogicArray("00000000001100"), \
                   LogicArray("00000010011000"), \
                   LogicArray("00000110011000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00011001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000010000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 4

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch1_sample58_output7(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=1, Sample=58
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 7
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00011110000000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 7

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch73_sample30_output6(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=73, Sample=30
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 6
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000001111000"), \
                   LogicArray("00000111111100"), \
                   LogicArray("00000110001000"), \
                   LogicArray("00001100000000"), \
                   LogicArray("00001100000000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001110110000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000011111000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 6

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch9_sample17_output9(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=9, Sample=17
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 9
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111000000"), \
    ]

    classification_result = 9

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch110_sample33_output1(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=110, Sample=33
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 1
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 1

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch104_sample44_output4(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=104, Sample=44
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 4
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000001000"), \
                   LogicArray("00000000011000"), \
                   LogicArray("00000000011000"), \
                   LogicArray("00000100111100"), \
                   LogicArray("00001101110000"), \
                   LogicArray("00011101100000"), \
                   LogicArray("00011011100000"), \
                   LogicArray("00011111100100"), \
                   LogicArray("00011111000100"), \
                   LogicArray("00000110000100"), \
                   LogicArray("00000100000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 4

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch133_sample1_output0(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=133, Sample=1
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 0
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00111111111110"), \
                   LogicArray("00111001111110"), \
                   LogicArray("00111000001110"), \
                   LogicArray("00111100011110"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 0

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch91_sample24_output1(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=91, Sample=24
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 1
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 1

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch55_sample11_output3(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=55, Sample=11
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 3
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 3

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch140_sample60_output8(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=140, Sample=60
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 8
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000111100"), \
                   LogicArray("00000011111100"), \
                   LogicArray("00000111111100"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00010111100000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00011111000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 8

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch15_sample32_output9(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=15, Sample=32
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 9
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00011101110000"), \
                   LogicArray("00011001110000"), \
                   LogicArray("00011101110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 9

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch18_sample59_output1(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=18, Sample=59
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 1
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000011000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000001111000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00000100000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 1

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch15_sample58_output8(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=15, Sample=58
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 8
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011111000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00011110011000"), \
                   LogicArray("00011100110000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00001110110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 8

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch121_sample9_output6(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=121, Sample=9
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 6
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 6

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch57_sample44_output7(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=57, Sample=44
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 7
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00001100000000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00011000111000"), \
                   LogicArray("00001000111000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000110000000"), \
    ]

    classification_result = 7

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch87_sample53_output8(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=87, Sample=53
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 8
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000011000"), \
                   LogicArray("00001110011000"), \
                   LogicArray("00011110111000"), \
                   LogicArray("00001101110000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 8

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch84_sample47_output8(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=84, Sample=47
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 8
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000011111000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 8

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch155_sample41_output6(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=155, Sample=41
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 6
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 6

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch39_sample57_output1(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=39, Sample=57
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 1
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 1

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch139_sample61_output3(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=139, Sample=61
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 3
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000001111000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("01111111110000"), \
                   LogicArray("01111111000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 3

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch24_sample9_output9(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=24, Sample=9
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 9
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00011111000000"), \
                   LogicArray("00111111100000"), \
                   LogicArray("00110001110000"), \
                   LogicArray("01110001111000"), \
                   LogicArray("00111111111000"), \
                   LogicArray("00011110111000"), \
                   LogicArray("00000000011000"), \
                   LogicArray("00000000011000"), \
                   LogicArray("00000000011000"), \
                   LogicArray("00000000011000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 9

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch40_sample8_output0(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=40, Sample=8
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 0
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00011111000000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00110001111000"), \
                   LogicArray("00110000011000"), \
                   LogicArray("00110000011100"), \
                   LogicArray("00110000001100"), \
                   LogicArray("00111000001100"), \
                   LogicArray("00011000001100"), \
                   LogicArray("00001111111100"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 0

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch135_sample45_output4(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=135, Sample=45
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 4
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000011000"), \
                   LogicArray("00000110011000"), \
                   LogicArray("00001110111000"), \
                   LogicArray("00001100110000"), \
                   LogicArray("00011101110000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 4

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch144_sample5_output0(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=144, Sample=5
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 0
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000001111000"), \
                   LogicArray("00000011111100"), \
                   LogicArray("00000111111100"), \
                   LogicArray("00001111111100"), \
                   LogicArray("00011111011100"), \
                   LogicArray("00111110111000"), \
                   LogicArray("00111100111000"), \
                   LogicArray("00111111110000"), \
                   LogicArray("00111111100000"), \
                   LogicArray("00111111000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 0

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch125_sample13_output6(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=125, Sample=13
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 6
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00011110000000"), \
                   LogicArray("00011101111100"), \
                   LogicArray("00011111111110"), \
                   LogicArray("00011111111110"), \
                   LogicArray("00011111111110"), \
                   LogicArray("00011111111110"), \
                   LogicArray("00001111111100"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 6

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch122_sample43_output6(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=122, Sample=43
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 6
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000011111000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00011111000000"), \
                   LogicArray("00011110000000"), \
                   LogicArray("00011100111100"), \
                   LogicArray("00011111111110"), \
                   LogicArray("00011111111110"), \
                   LogicArray("00001111111100"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 6

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch147_sample36_output1(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=147, Sample=36
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 1
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 1

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch111_sample56_output5(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=111, Sample=56
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 5
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000011100"), \
                   LogicArray("00000001111110"), \
                   LogicArray("00000011111110"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00011110000000"), \
                   LogicArray("00001000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 5

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch110_sample18_output6(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=110, Sample=18
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 6
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00001100000000"), \
                   LogicArray("00001100111000"), \
                   LogicArray("00011101111000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 6

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch92_sample13_output6(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=92, Sample=13
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 6
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 6

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch70_sample57_output3(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=70, Sample=57
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 3
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00011101110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00001000111000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 3

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch100_sample29_output0(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=100, Sample=29
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 0
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011111000"), \
                   LogicArray("00000111111100"), \
                   LogicArray("00001111101110"), \
                   LogicArray("00011111001110"), \
                   LogicArray("00011100001110"), \
                   LogicArray("00111000001110"), \
                   LogicArray("00111000011100"), \
                   LogicArray("00111000111100"), \
                   LogicArray("00111111111000"), \
                   LogicArray("00111111110000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 0

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch30_sample22_output8(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=30, Sample=22
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 8
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011111000"), \
                   LogicArray("00000110011000"), \
                   LogicArray("00001100011000"), \
                   LogicArray("00001100010000"), \
                   LogicArray("00001100110000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 8

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch37_sample23_output2(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=37, Sample=23
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 2
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000011111000"), \
                   LogicArray("00000011111000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00011110111000"), \
                   LogicArray("00011100000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 2

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch85_sample63_output9(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=85, Sample=63
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 9
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00011100111000"), \
                   LogicArray("00111011111000"), \
                   LogicArray("00111111111000"), \
                   LogicArray("00011101110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000110000000"), \
    ]

    classification_result = 9

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch82_sample62_output7(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=82, Sample=62
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 7
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00111111111000"), \
                   LogicArray("00111111111000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000001111000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00001110000000"), \
    ]

    classification_result = 7

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch13_sample53_output6(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=13, Sample=53
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 6
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 6

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch119_sample23_output3(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=119, Sample=23
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 3
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000000011000"), \
                   LogicArray("00000000011100"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 3

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch18_sample62_output1(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=18, Sample=62
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 1
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000010000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 1

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch80_sample41_output6(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=80, Sample=41
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 6
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00001100000000"), \
                   LogicArray("00011100001100"), \
                   LogicArray("00011100011100"), \
                   LogicArray("00011101111110"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00001111111100"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 6

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch64_sample55_output7(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=64, Sample=55
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 7
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00111111111000"), \
                   LogicArray("00111001111100"), \
                   LogicArray("00111000011100"), \
                   LogicArray("00111000011100"), \
                   LogicArray("00000000111100"), \
                   LogicArray("00000001111000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
    ]

    classification_result = 7

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch110_sample62_output4(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=110, Sample=62
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 4
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000011000"), \
                   LogicArray("00000011011000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000110110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000010000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 4

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch71_sample50_output2(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=71, Sample=50
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 2
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000000011000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00011110111000"), \
                   LogicArray("00011000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 2

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch38_sample54_output6(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=38, Sample=54
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 6
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00001100111000"), \
                   LogicArray("00001101111100"), \
                   LogicArray("00001111111100"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 6

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch112_sample50_output4(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=112, Sample=50
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 4
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000001100"), \
                   LogicArray("00000110001100"), \
                   LogicArray("00000110011000"), \
                   LogicArray("00001100111000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00111111111100"), \
                   LogicArray("00010011100100"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000100000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 4

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch141_sample52_output6(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=141, Sample=52
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 6
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00011111111110"), \
                   LogicArray("00011111111110"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 6

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch96_sample29_output9(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=96, Sample=29
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 9
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011111100"), \
                   LogicArray("00000111111100"), \
                   LogicArray("00001111111100"), \
                   LogicArray("00011110011100"), \
                   LogicArray("00011100011100"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00111111100000"), \
                   LogicArray("00111110000000"), \
                   LogicArray("00111000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 9

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch85_sample20_output1(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=85, Sample=20
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 1
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 1

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch140_sample37_output6(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=140, Sample=37
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 6
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00001100111000"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 6

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch102_sample51_output4(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=102, Sample=51
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 4
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000011000"), \
                   LogicArray("00000100011000"), \
                   LogicArray("00000100011000"), \
                   LogicArray("00001000110000"), \
                   LogicArray("00011001111000"), \
                   LogicArray("00111111111000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 4

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch57_sample24_output4(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=57, Sample=24
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 4
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000110110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00001011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 4

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch89_sample45_output4(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=89, Sample=45
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 4
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000110001100"), \
                   LogicArray("00000110011100"), \
                   LogicArray("00001100011000"), \
                   LogicArray("00001100011000"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00111111111000"), \
                   LogicArray("00111101110000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 4

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch105_sample35_output8(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=105, Sample=35
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 8
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011111100"), \
                   LogicArray("00000111111100"), \
                   LogicArray("00000111111100"), \
                   LogicArray("00000111111100"), \
                   LogicArray("00000011111000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00011111000000"), \
                   LogicArray("00111110000000"), \
                   LogicArray("00111000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 8

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch27_sample40_output0(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=27, Sample=40
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 0
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000011111000"), \
                   LogicArray("00000111101100"), \
                   LogicArray("00001111001100"), \
                   LogicArray("00001110001100"), \
                   LogicArray("00001100001100"), \
                   LogicArray("00011100001000"), \
                   LogicArray("00011000011000"), \
                   LogicArray("00011000110000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 0

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch38_sample12_output1(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=38, Sample=12
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 1
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000001000000"), \
                   LogicArray("00000001000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000001000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 1

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch129_sample59_output2(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=129, Sample=59
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 2
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000111111110"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00111111000000"), \
                   LogicArray("00111110000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 2

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch12_sample10_output5(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=12, Sample=10
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 5
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00011111000000"), \
                   LogicArray("00011100000000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00000001111000"), \
                   LogicArray("00000000111100"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 5

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch37_sample43_output1(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=37, Sample=43
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 1
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 1

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch134_sample20_output9(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=134, Sample=20
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 9
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001100111000"), \
                   LogicArray("00011101111000"), \
                   LogicArray("00011001110000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 9

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch146_sample2_output2(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=146, Sample=2
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 2
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000000011000"), \
                   LogicArray("00000000011000"), \
                   LogicArray("00000111011000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00011101110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 2

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch38_sample4_output4(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=38, Sample=4
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 4
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00110001110000"), \
                   LogicArray("00110001110100"), \
                   LogicArray("00111000111100"), \
                   LogicArray("00111000111100"), \
                   LogicArray("00111111111100"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00001111111100"), \
                   LogicArray("00000000011100"), \
                   LogicArray("00000000011100"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 4

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch147_sample50_output7(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=147, Sample=50
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 7
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00011100111000"), \
                   LogicArray("00111000111000"), \
                   LogicArray("00111000111000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
    ]

    classification_result = 7

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch49_sample36_output4(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=49, Sample=36
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 4
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00001111011000"), \
                   LogicArray("00011110011000"), \
                   LogicArray("00011100011000"), \
                   LogicArray("00111111011000"), \
                   LogicArray("00111111111000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000000010000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 4

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch116_sample52_output3(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=116, Sample=52
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 3
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00010001110000"), \
                   LogicArray("00111011100000"), \
                   LogicArray("00111111000000"), \
                   LogicArray("00011110000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 3

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch98_sample36_output1(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=98, Sample=36
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 1
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 1

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch104_sample18_output7(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=104, Sample=18
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 7
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00001111111100"), \
                   LogicArray("00111111111100"), \
                   LogicArray("00111000011000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00001100000000"), \
    ]

    classification_result = 7

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch28_sample22_output7(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=28, Sample=22
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 7
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000001100"), \
                   LogicArray("00000011111100"), \
                   LogicArray("00111111111000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000110000000"), \
    ]

    classification_result = 7

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch62_sample3_output4(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=62, Sample=3
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 4
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111000110"), \
                   LogicArray("00001111011110"), \
                   LogicArray("00011110111100"), \
                   LogicArray("00111001111000"), \
                   LogicArray("00111111111100"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 4

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch112_sample61_output2(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=112, Sample=61
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 2
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001000111000"), \
                   LogicArray("00001011111000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00011110011110"), \
                   LogicArray("00011000000110"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 2

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch44_sample47_output9(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=44, Sample=47
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 9
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 9

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch131_sample1_output6(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=131, Sample=1
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 6
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00001110111000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 6

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch91_sample61_output5(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=91, Sample=61
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 5
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001100000000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000000011000"), \
                   LogicArray("00011100011000"), \
                   LogicArray("00011110110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 5

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch78_sample10_output9(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=78, Sample=10
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 9
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011111000"), \
                   LogicArray("00000111111100"), \
                   LogicArray("00001110111100"), \
                   LogicArray("00011101111000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 9

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch99_sample47_output0(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=99, Sample=47
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 0
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000110111000"), \
                   LogicArray("00001110011000"), \
                   LogicArray("00001110011000"), \
                   LogicArray("00001100011000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 0

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch7_sample26_output8(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=7, Sample=26
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 8
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000011000"), \
                   LogicArray("00000011111000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001110111000"), \
                   LogicArray("00001100110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 8

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch52_sample47_output2(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=52, Sample=47
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 2
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000001111000"), \
                   LogicArray("00000001111000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00111111000000"), \
                   LogicArray("00111111110000"), \
                   LogicArray("00111111110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 2

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch35_sample41_output3(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=35, Sample=41
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 3
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00001001100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000001111000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 3

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch130_sample21_output6(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=130, Sample=21
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 6
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00011100000000"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00111111111110"), \
                   LogicArray("00111111011110"), \
                   LogicArray("00111111111100"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 6

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch123_sample62_output1(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=123, Sample=62
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 1
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000001111000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 1

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch100_sample8_output1(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=100, Sample=8
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 1
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000010000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 1

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch20_sample46_output7(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=20, Sample=46
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 7
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000000011000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00011100000000"), \
                   LogicArray("00011100000000"), \
                   LogicArray("00011000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 7

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch132_sample7_output7(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=132, Sample=7
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 7
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("01111111000000"), \
                   LogicArray("01111111111000"), \
                   LogicArray("01100111111000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
    ]

    classification_result = 7

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch33_sample28_output6(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=33, Sample=28
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 6
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00011000000000"), \
                   LogicArray("00011000000000"), \
                   LogicArray("00011000000000"), \
                   LogicArray("00011000011000"), \
                   LogicArray("00011001111100"), \
                   LogicArray("00011001111110"), \
                   LogicArray("00011001100110"), \
                   LogicArray("00011101101110"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 6

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch126_sample36_output1(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=126, Sample=36
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 1
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 1

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch97_sample32_output2(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=97, Sample=32
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 2
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00111111111000"), \
                   LogicArray("00111111111000"), \
                   LogicArray("00111100010000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 2

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch114_sample26_output9(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=114, Sample=26
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 9
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001101110000"), \
                   LogicArray("00001101110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 9

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch140_sample7_output6(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=140, Sample=7
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 6
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001110111000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 6

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch134_sample38_output0(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=134, Sample=38
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 0
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000011111000"), \
                   LogicArray("00000111011000"), \
                   LogicArray("00000110011000"), \
                   LogicArray("00001110001100"), \
                   LogicArray("00001100001100"), \
                   LogicArray("00011100011000"), \
                   LogicArray("00011100111000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 0

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch108_sample55_output9(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=108, Sample=55
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 9
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011111000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00001101110000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 9

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch86_sample29_output7(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=86, Sample=29
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 7
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001110111000"), \
                   LogicArray("00001101110000"), \
                   LogicArray("00001101110000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000110000000"), \
    ]

    classification_result = 7

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch11_sample7_output5(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=11, Sample=7
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 5
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111111110"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00000011111000"), \
                   LogicArray("00000000011000"), \
                   LogicArray("00111100111000"), \
                   LogicArray("00111111110000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 5

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch6_sample43_output1(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=6, Sample=43
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 1
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 1

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch66_sample30_output5(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=66, Sample=30
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 5
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011111110"), \
                   LogicArray("00000011111110"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00110001100000"), \
                   LogicArray("00111111100000"), \
                   LogicArray("00011110000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 5

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch30_sample13_output7(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=30, Sample=13
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 7
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00111111110000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000010000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 7

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch153_sample56_output1(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=153, Sample=56
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 1
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000010000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000001111000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00011100000000"), \
                   LogicArray("00001000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 1

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch78_sample8_output3(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=78, Sample=8
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 3
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00001001100000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00010000111000"), \
                   LogicArray("00000000011000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 3

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch49_sample28_output6(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=49, Sample=28
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 6
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00001100000000"), \
                   LogicArray("00011100111000"), \
                   LogicArray("00011001111100"), \
                   LogicArray("00011001111100"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 6

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch24_sample60_output9(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=24, Sample=60
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 9
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00001101100000"), \
                   LogicArray("00001100110000"), \
                   LogicArray("00011001110000"), \
                   LogicArray("00011001100000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000000100000"), \
                   LogicArray("00000000100000"), \
                   LogicArray("00000000100000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 9

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch72_sample7_output2(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=72, Sample=7
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 2
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00111111111110"), \
                   LogicArray("00111111111100"), \
                   LogicArray("00111111100000"), \
                   LogicArray("00011110000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 2

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch105_sample62_output6(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=105, Sample=62
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 6
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000011000"), \
                   LogicArray("00000001111000"), \
                   LogicArray("00000011111000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00011110111000"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00111111111000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 6

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch115_sample4_output2(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=115, Sample=4
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 2
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00111111111000"), \
                   LogicArray("00111111111100"), \
                   LogicArray("00111110011100"), \
                   LogicArray("00011000001100"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 2

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch50_sample18_output6(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=50, Sample=18
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 6
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000001000"), \
                   LogicArray("00000000111100"), \
                   LogicArray("00000001111000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00011110110000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 6

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch89_sample55_output7(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=89, Sample=55
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 7
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00010000111000"), \
                   LogicArray("00111111111100"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00000001111000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00011110000000"), \
                   LogicArray("00011100000000"), \
    ]

    classification_result = 7

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch148_sample16_output0(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=148, Sample=16
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 0
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00001111111100"), \
                   LogicArray("00011110111110"), \
                   LogicArray("00111000001110"), \
                   LogicArray("00110000000110"), \
                   LogicArray("00111000011110"), \
                   LogicArray("00111111111100"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 0

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch148_sample21_output5(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=148, Sample=21
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 5
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000011100"), \
                   LogicArray("00001111111110"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00011111000000"), \
                   LogicArray("00011111000000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000001111000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 5

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch88_sample39_output9(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=88, Sample=39
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 9
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
    ]

    classification_result = 9

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch78_sample43_output0(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=78, Sample=43
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 0
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000001111000"), \
                   LogicArray("00000111111100"), \
                   LogicArray("00001111111110"), \
                   LogicArray("00011111001110"), \
                   LogicArray("00111110001110"), \
                   LogicArray("00111100111100"), \
                   LogicArray("00111111111000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 0

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch146_sample35_output2(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=146, Sample=35
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 2
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00011100111100"), \
                   LogicArray("00011100011100"), \
                   LogicArray("00000011111100"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00111111111100"), \
                   LogicArray("00111111111100"), \
                   LogicArray("00111111100000"), \
                   LogicArray("00111110000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 2

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch84_sample37_output8(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=84, Sample=37
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 8
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000110110000"), \
                   LogicArray("00000110110000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 8

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch66_sample19_output6(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=66, Sample=19
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 6
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000001111000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 6

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch2_sample48_output1(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=2, Sample=48
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 1
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000001000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000010000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 1

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch102_sample46_output2(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=102, Sample=46
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 2
    # --------------------------------------------
    input_image = [LogicArray("00011000000000"), \
                   LogicArray("00010000111000"), \
                   LogicArray("00000000011000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000011000"), \
                   LogicArray("00000000011000"), \
                   LogicArray("00000000011000"), \
                   LogicArray("00000111111100"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 2

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch55_sample41_output4(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=55, Sample=41
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 4
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000100000000"), \
                   LogicArray("00000100010000"), \
                   LogicArray("00000100110000"), \
                   LogicArray("00000100110000"), \
                   LogicArray("00000101110000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 4

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch19_sample3_output8(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=19, Sample=3
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 8
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001110110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000011111000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 8

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch39_sample36_output6(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=39, Sample=36
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 6
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000010000000"), \
                   LogicArray("00000010000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 6

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch65_sample13_output2(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=65, Sample=13
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 2
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00111111100000"), \
                   LogicArray("00110111110000"), \
                   LogicArray("00111110110000"), \
                   LogicArray("00001100011000"), \
                   LogicArray("00000000001000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 2

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch136_sample39_output4(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=136, Sample=39
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 4
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000001000"), \
                   LogicArray("00000110011100"), \
                   LogicArray("00001110011000"), \
                   LogicArray("00001110111000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 4

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch57_sample43_output5(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=57, Sample=43
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 5
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001100000000"), \
                   LogicArray("00001100000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00000111111100"), \
                   LogicArray("00011000111100"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 5

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch42_sample23_output6(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=42, Sample=23
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 6
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00110000000000"), \
                   LogicArray("00110000000000"), \
                   LogicArray("00110000000000"), \
                   LogicArray("00110000000000"), \
                   LogicArray("00111001111100"), \
                   LogicArray("00111001111110"), \
                   LogicArray("00011011101110"), \
                   LogicArray("00011111111110"), \
                   LogicArray("00001111111100"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 6

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch70_sample0_output9(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=70, Sample=0
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 9
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00111111111100"), \
                   LogicArray("00111111110000"), \
                   LogicArray("00111111110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
    ]

    classification_result = 9

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch76_sample38_output5(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=76, Sample=38
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 5
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000001111000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00001011100000"), \
                   LogicArray("00011111000000"), \
                   LogicArray("00011110000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 5

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch90_sample4_output3(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=90, Sample=4
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 3
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000110111000"), \
                   LogicArray("00011000110000"), \
                   LogicArray("00011011110000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 3

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch86_sample45_output7(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=86, Sample=45
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 7
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00011101111000"), \
                   LogicArray("00011000111000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
    ]

    classification_result = 7

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch128_sample26_output7(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=128, Sample=26
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 7
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001100110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00001100000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 7

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch140_sample18_output0(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=140, Sample=18
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 0
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000111111100"), \
                   LogicArray("00001111111100"), \
                   LogicArray("00001110001100"), \
                   LogicArray("00011100001100"), \
                   LogicArray("00111000011100"), \
                   LogicArray("00111000111100"), \
                   LogicArray("00111111111000"), \
                   LogicArray("00111111110000"), \
                   LogicArray("00011110000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 0

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch147_sample33_output6(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=147, Sample=33
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 6
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00001100000000"), \
                   LogicArray("00001101111000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001111011000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 6

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch82_sample8_output4(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=82, Sample=8
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 4
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000100001000"), \
                   LogicArray("00001110001100"), \
                   LogicArray("00001100011100"), \
                   LogicArray("00011100011000"), \
                   LogicArray("00111000111000"), \
                   LogicArray("00111100111000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000001000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 4

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch140_sample46_output2(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=140, Sample=46
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 2
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011111000"), \
                   LogicArray("00001111111100"), \
                   LogicArray("00001111111100"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00001111001100"), \
                   LogicArray("00011111111110"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00111111100000"), \
                   LogicArray("00011100000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 2

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch95_sample39_output7(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=95, Sample=39
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 7
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000001111000"), \
                   LogicArray("00111111111000"), \
                   LogicArray("00111111111000"), \
                   LogicArray("00111101111000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111000000"), \
    ]

    classification_result = 7

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch9_sample31_output6(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=9, Sample=31
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 6
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00001100111000"), \
                   LogicArray("00001111111100"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001111011000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 6

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch64_sample17_output2(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=64, Sample=17
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 2
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00011110000000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00010011100000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00000110011000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 2

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch84_sample17_output4(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=84, Sample=17
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 4
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000011000"), \
                   LogicArray("00001100011000"), \
                   LogicArray("00001100011000"), \
                   LogicArray("00011100111000"), \
                   LogicArray("00011000110000"), \
                   LogicArray("00011101110000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 4

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch84_sample14_output2(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=84, Sample=14
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 2
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011111000"), \
                   LogicArray("00000011111000"), \
                   LogicArray("00000000011100"), \
                   LogicArray("00000000011100"), \
                   LogicArray("00111100011100"), \
                   LogicArray("01111111111000"), \
                   LogicArray("01111111111000"), \
                   LogicArray("01111111111000"), \
                   LogicArray("00111111011000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 2

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch149_sample8_output9(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=149, Sample=8
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 9
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001101111000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00000110000000"), \
    ]

    classification_result = 9

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch59_sample53_output8(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=59, Sample=53
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 8
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001110001100"), \
                   LogicArray("00001110011100"), \
                   LogicArray("00000111111100"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00111000110000"), \
                   LogicArray("00111111110000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 8

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch129_sample19_output5(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=129, Sample=19
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 5
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011111111"), \
                   LogicArray("00000111111110"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00011001100000"), \
                   LogicArray("00011011100000"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 5

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch34_sample18_output6(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=34, Sample=18
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 6
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000111100"), \
                   LogicArray("00000011111000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00001100000000"), \
                   LogicArray("00011100000000"), \
                   LogicArray("00001111111100"), \
                   LogicArray("00001111111100"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 6

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch11_sample33_output6(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=11, Sample=33
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 6
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00011100000000"), \
                   LogicArray("00011000000000"), \
                   LogicArray("00011000011110"), \
                   LogicArray("00011000111110"), \
                   LogicArray("00011100111110"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 6

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch26_sample3_output1(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=26, Sample=3
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 1
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 1

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch143_sample20_output7(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=143, Sample=20
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 7
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00011000000000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00011100111000"), \
                   LogicArray("00000001111000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 7

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch15_sample40_output9(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=15, Sample=40
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 9
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00001100000000"), \
                   LogicArray("00001000000000"), \
    ]

    classification_result = 9

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch101_sample11_output4(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=101, Sample=11
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 4
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000001100"), \
                   LogicArray("00000000001100"), \
                   LogicArray("00001110011100"), \
                   LogicArray("00001110011000"), \
                   LogicArray("00011100111000"), \
                   LogicArray("00011100111100"), \
                   LogicArray("00111111111100"), \
                   LogicArray("00111111100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 4

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch107_sample4_output7(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=107, Sample=4
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 7
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000001000000"), \
    ]

    classification_result = 7

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch127_sample11_output2(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=127, Sample=11
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 2
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00111111111100"), \
                   LogicArray("00111111111110"), \
                   LogicArray("00111000111000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 2

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch115_sample1_output4(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=115, Sample=1
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 4
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000010110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 4

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')


@cocotb.test()
async def test_mnist_batch62_sample57_output1(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: Batch=62, Sample=57
    # Author: estods3
    # Input: described in 'input_image'
    # Expected Result: BCD = 1
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 1

    # PERFORM TEST
    # ------------
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units='us')
    cocotb.start_soon(clock.start())

    # Initial Conditions
    dut.ena.value = 1
    dut.ui_in.value = 128
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    assert int(dut.uo_out[7].value) == 0      # Confirm Outputs Invalid (flag = 0) before Image is Transmitted

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for row in input_image:
        dut.ui_in.value = 128 + row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 50)

    # Evaluate Results
    # ----------------
    dut._log.info('Evaluating...')
    #print(dut.uo_out.value)
    #print(dut.uio_out.value)
    #print(dut.uio_oe.value)
    assert int(dut.uo_out[7].value) == 1  #Test Classification Flag set to 1
    assert int(dut.uio_oe.value) == 0xFF  #Test All Bidirectional I/O Output Enable set to '1'
    assert int(dut.uio_out.value) == classification_result
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        assert int(dut.uo_out.value[1:7]) == segments[classification_result]
    else:
        assert int(dut.uo_out.value[6:0]) == segments[classification_result]
    dut._log.info('Evaluating...Done')