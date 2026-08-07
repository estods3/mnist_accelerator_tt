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
async def test_mnist_batch_set(dut):
    # THIS TEST WAS AUTOGENERATED USING utility.py
    # Test: All samples run as subtests within a single cocotb test
    # Author: estods3
    # Pass Criteria: (subtests passed / subtests tried) >= 0.8
    # --------------------------------------------

    THRESHOLD = 0.8
    subtests_tried = 0
    subtests_passed = 0
    failed_subtests = []

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

    # --------------------------------------------
    # Subtest: Batch=45, Sample=37, Expected BCD=4
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000010000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000010110000"), \
                   LogicArray("00000110110000"), \
                   LogicArray("00000110110000"), \
                   LogicArray("00001101110000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000101110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 4

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((45, 37))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=68, Sample=27, Expected BCD=4
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00001110110000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00001000110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 4

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((68, 27))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=37, Sample=41, Expected BCD=1
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00001100000000"), \
                   LogicArray("00001000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 1

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((37, 41))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=2, Sample=4, Expected BCD=5
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000011111000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00011110000000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000001111100"), \
                   LogicArray("00001111111100"), \
                   LogicArray("00001111111100"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 5

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((2, 4))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=6, Sample=59, Expected BCD=0
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000110110000"), \
                   LogicArray("00000110110000"), \
                   LogicArray("00000110110000"), \
                   LogicArray("00000110110000"), \
                   LogicArray("00000110110000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 0

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((6, 59))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=152, Sample=37, Expected BCD=7
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000001000000"), \
                   LogicArray("00110011111100"), \
                   LogicArray("00000111111100"), \
                   LogicArray("00001110111000"), \
                   LogicArray("00001100110000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00001100000000"), \
                   LogicArray("00011100000000"), \
    ]

    classification_result = 7

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((152, 37))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=150, Sample=54, Expected BCD=3
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111111100"), \
                   LogicArray("00001111111100"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("01100001110000"), \
                   LogicArray("01111111100000"), \
                   LogicArray("00111111000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 3

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((150, 54))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=139, Sample=6, Expected BCD=2
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00111111110000"), \
                   LogicArray("00111111111000"), \
                   LogicArray("00011100111000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 2

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((139, 6))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=150, Sample=27, Expected BCD=6
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000011000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000001111000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00001111010000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00011111000000"), \
                   LogicArray("00011100000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 6

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((150, 27))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=115, Sample=29, Expected BCD=6
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00001110110000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 6

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((115, 29))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=50, Sample=2, Expected BCD=7
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00011111001000"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000010000000"), \
    ]

    classification_result = 7

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((50, 2))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=75, Sample=32, Expected BCD=6
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 6

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((75, 32))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=120, Sample=45, Expected BCD=1
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 1

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((120, 45))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=149, Sample=46, Expected BCD=3
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000011111000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00111111100000"), \
                   LogicArray("00111111000000"), \
                   LogicArray("00001000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 3

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((149, 46))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=10, Sample=53, Expected BCD=8
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000010000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 8

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((10, 53))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=49, Sample=52, Expected BCD=4
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000011000"), \
                   LogicArray("00000110011000"), \
                   LogicArray("00000110011000"), \
                   LogicArray("00001100011000"), \
                   LogicArray("00011100110000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00111111110000"), \
                   LogicArray("00010001110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 4

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((49, 52))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=90, Sample=2, Expected BCD=1
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
                   LogicArray("00000111000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 1

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((90, 2))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=10, Sample=12, Expected BCD=1
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 1

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((10, 12))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=95, Sample=52, Expected BCD=2
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00001111111100"), \
                   LogicArray("00011111111110"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00001100000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 2

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((95, 52))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=15, Sample=37, Expected BCD=0
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000001111100"), \
                   LogicArray("00000111111110"), \
                   LogicArray("00001111111100"), \
                   LogicArray("00011111011100"), \
                   LogicArray("00011111011100"), \
                   LogicArray("00111100011100"), \
                   LogicArray("00111000011100"), \
                   LogicArray("00111001111100"), \
                   LogicArray("00111111111000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 0

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((15, 37))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=37, Sample=56, Expected BCD=3
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000010000000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00010000110000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 3

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((37, 56))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=149, Sample=19, Expected BCD=6
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00001110111000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 6

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((149, 19))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=49, Sample=36, Expected BCD=4
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
                   LogicArray("00000000011000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 4

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((49, 36))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=59, Sample=46, Expected BCD=6
    # --------------------------------------------
    input_image = [LogicArray("00000010000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00001100000000"), \
                   LogicArray("00011100000000"), \
                   LogicArray("00011100011110"), \
                   LogicArray("00011001111110"), \
                   LogicArray("00011001111110"), \
                   LogicArray("00011101111100"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 6

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((59, 46))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=51, Sample=61, Expected BCD=0
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001111111100"), \
                   LogicArray("00011110011100"), \
                   LogicArray("00011100011100"), \
                   LogicArray("00011100011100"), \
                   LogicArray("00011100111000"), \
                   LogicArray("00011101111000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000010000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 0

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((51, 61))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=23, Sample=37, Expected BCD=4
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000011000"), \
                   LogicArray("00011000111000"), \
                   LogicArray("00111000011000"), \
                   LogicArray("00110000111000"), \
                   LogicArray("01111111111000"), \
                   LogicArray("00111111111000"), \
                   LogicArray("00011001110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 4

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((23, 37))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=40, Sample=34, Expected BCD=3
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000100111000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 3

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((40, 34))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=8, Sample=8, Expected BCD=8
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000100000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000011111100"), \
                   LogicArray("00000011011100"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 8

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((8, 8))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=53, Sample=51, Expected BCD=3
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000010000000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00000000011000"), \
                   LogicArray("00000100011000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 3

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((53, 51))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=38, Sample=25, Expected BCD=4
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00001110010000"), \
                   LogicArray("00001110111000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 4

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((38, 25))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=76, Sample=50, Expected BCD=6
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00011100000000"), \
                   LogicArray("00011000010000"), \
                   LogicArray("00111011111100"), \
                   LogicArray("00111011111110"), \
                   LogicArray("00111111001110"), \
                   LogicArray("00011111111110"), \
                   LogicArray("00001111111100"), \
                   LogicArray("00000011111000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 6

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((76, 50))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=50, Sample=11, Expected BCD=1
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 1

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((50, 11))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=55, Sample=5, Expected BCD=7
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00011111111110"), \
                   LogicArray("00000000011110"), \
                   LogicArray("00000000111100"), \
                   LogicArray("00000011111000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00111110000000"), \
                   LogicArray("00111100000000"), \
                   LogicArray("00111000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 7

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((55, 5))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=108, Sample=60, Expected BCD=8
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00001111111100"), \
                   LogicArray("00001111111100"), \
                   LogicArray("00001100111100"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 8

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((108, 60))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=96, Sample=27, Expected BCD=7
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00001110000000"), \
    ]

    classification_result = 7

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((96, 27))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=51, Sample=8, Expected BCD=1
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 1

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((51, 8))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=92, Sample=33, Expected BCD=2
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001101110000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00011110110000"), \
                   LogicArray("00001100000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 2

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((92, 33))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=27, Sample=27, Expected BCD=5
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000010000"), \
                   LogicArray("00000011111000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00011011110000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00011111000000"), \
                   LogicArray("00001100000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 5

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((27, 27))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=47, Sample=18, Expected BCD=1
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00001100000000"), \
                   LogicArray("00011000000000"), \
                   LogicArray("00010000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 1

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((47, 18))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=148, Sample=46, Expected BCD=1
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
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 1

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((148, 46))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=18, Sample=48, Expected BCD=8
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000001000000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00001101100000"), \
                   LogicArray("00011101100000"), \
                   LogicArray("00011001100000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 8

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((18, 48))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=154, Sample=14, Expected BCD=5
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000001111100"), \
                   LogicArray("00000011111100"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 5

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((154, 14))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=103, Sample=3, Expected BCD=8
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000001111100"), \
                   LogicArray("00000111111100"), \
                   LogicArray("00001110011100"), \
                   LogicArray("00001110111000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 8

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((103, 3))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=10, Sample=3, Expected BCD=2
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00111111110000"), \
                   LogicArray("00010001110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00001111111100"), \
                   LogicArray("00011111111110"), \
                   LogicArray("00011110000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 2

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((10, 3))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=152, Sample=19, Expected BCD=5
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000001111110"), \
                   LogicArray("00000011111100"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000100110000"), \
                   LogicArray("00111001110000"), \
                   LogicArray("00111111100000"), \
                   LogicArray("00011111000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 5

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((152, 19))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=63, Sample=63, Expected BCD=9
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00011101111000"), \
                   LogicArray("00111111110000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00001100110000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 9

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((63, 63))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=40, Sample=13, Expected BCD=5
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 5

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((40, 13))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=121, Sample=21, Expected BCD=8
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00001111111100"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 8

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((121, 21))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=154, Sample=45, Expected BCD=9
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000001111000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00001110111000"), \
                   LogicArray("00001100111000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 9

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((154, 45))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=49, Sample=21, Expected BCD=5
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00011110000000"), \
                   LogicArray("00011111000000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00111111110000"), \
                   LogicArray("00111110111000"), \
                   LogicArray("00011000011100"), \
                   LogicArray("00000000001100"), \
                   LogicArray("00000000001100"), \
                   LogicArray("00011000111100"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 5

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((49, 21))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=31, Sample=8, Expected BCD=9
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00001110111000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 9

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((31, 8))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=2, Sample=13, Expected BCD=7
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("11111111111000"), \
                   LogicArray("11111111111000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000000110000"), \
    ]

    classification_result = 7

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((2, 13))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=101, Sample=19, Expected BCD=5
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000111110"), \
                   LogicArray("00000011111110"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00011001110000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 5

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((101, 19))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=100, Sample=63, Expected BCD=6
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000001111000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00001111111100"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00011111001100"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 6

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((100, 63))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=70, Sample=34, Expected BCD=4
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000011000"), \
                   LogicArray("00000011011000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 4

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((70, 34))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=64, Sample=19, Expected BCD=2
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00011011110000"), \
                   LogicArray("00011011111000"), \
                   LogicArray("00011111011000"), \
                   LogicArray("00011110000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 2

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((64, 19))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=112, Sample=17, Expected BCD=3
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00111111111000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000011111000"), \
                   LogicArray("00000000011000"), \
                   LogicArray("00000000011000"), \
                   LogicArray("00011000111000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 3

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((112, 17))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=147, Sample=58, Expected BCD=9
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000100000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00001101110000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 9

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((147, 58))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=43, Sample=27, Expected BCD=0
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00011110011100"), \
                   LogicArray("00011110011100"), \
                   LogicArray("00011100001100"), \
                   LogicArray("00111000001110"), \
                   LogicArray("00111000001110"), \
                   LogicArray("00111000001100"), \
                   LogicArray("00011100011100"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 0

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((43, 27))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=126, Sample=6, Expected BCD=3
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000011111000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 3

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((126, 6))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=113, Sample=55, Expected BCD=8
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000001000000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000111111100"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00000100000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 8

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((113, 55))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=26, Sample=50, Expected BCD=9
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001111000"), \
                   LogicArray("00000001111000"), \
                   LogicArray("00000000100000"), \
    ]

    classification_result = 9

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((26, 50))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=95, Sample=56, Expected BCD=5
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111111111"), \
                   LogicArray("00000111111111"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 5

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((95, 56))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=121, Sample=11, Expected BCD=8
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011111100"), \
                   LogicArray("00000111111100"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 8

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((121, 11))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=26, Sample=6, Expected BCD=5
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00001100001100"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00111111110000"), \
                   LogicArray("00111111100000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 5

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((26, 6))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=65, Sample=53, Expected BCD=9
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00011101111000"), \
                   LogicArray("00011101111000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 9

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((65, 53))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=106, Sample=60, Expected BCD=2
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000010000000"), \
                   LogicArray("00011111000000"), \
                   LogicArray("00111111100000"), \
                   LogicArray("00110011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00001111111110"), \
                   LogicArray("00000011111110"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 2

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((106, 60))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=8, Sample=37, Expected BCD=2
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00011000011000"), \
                   LogicArray("00000000011100"), \
                   LogicArray("00000000011100"), \
                   LogicArray("00011000011100"), \
                   LogicArray("00111111111000"), \
                   LogicArray("00111111111000"), \
                   LogicArray("00111111111100"), \
                   LogicArray("00111111000000"), \
                   LogicArray("00001000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 2

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((8, 37))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=92, Sample=23, Expected BCD=8
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001100110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001101100000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 8

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((92, 23))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=102, Sample=6, Expected BCD=2
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001100110000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00011100000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 2

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((102, 6))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=63, Sample=18, Expected BCD=1
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000001000000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001000000"), \
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

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((63, 18))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=96, Sample=30, Expected BCD=3
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000010000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00001111111100"), \
                   LogicArray("00011100111100"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 3

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((96, 30))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=6, Sample=21, Expected BCD=4
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00011001100000"), \
                   LogicArray("00111001110000"), \
                   LogicArray("00111001110000"), \
                   LogicArray("00111001110000"), \
                   LogicArray("00111111111000"), \
                   LogicArray("00111111111000"), \
                   LogicArray("00111111111000"), \
                   LogicArray("00000000111100"), \
                   LogicArray("00000000011100"), \
                   LogicArray("00000000011100"), \
                   LogicArray("00000000011100"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 4

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((6, 21))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=111, Sample=43, Expected BCD=2
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00001111111110"), \
                   LogicArray("00011111111110"), \
                   LogicArray("00011111000000"), \
                   LogicArray("00011110000000"), \
                   LogicArray("00001000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 2

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((111, 43))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=94, Sample=26, Expected BCD=5
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00111111111000"), \
                   LogicArray("00111111110000"), \
                   LogicArray("00111011111000"), \
                   LogicArray("00111111111000"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00000110001100"), \
                   LogicArray("00000110011100"), \
                   LogicArray("00000111111100"), \
                   LogicArray("00000111111100"), \
                   LogicArray("00000001111000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 5

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((94, 26))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=123, Sample=47, Expected BCD=8
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00001111111110"), \
                   LogicArray("00011111111110"), \
                   LogicArray("00011111111110"), \
                   LogicArray("00001111111100"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00111111110000"), \
                   LogicArray("00111111110000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 8

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((123, 47))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=23, Sample=42, Expected BCD=2
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001110111000"), \
                   LogicArray("00001000111000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00001110001100"), \
                   LogicArray("00001111111100"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 2

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((23, 42))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=60, Sample=7, Expected BCD=0
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00011100111100"), \
                   LogicArray("00011000001100"), \
                   LogicArray("00110000001100"), \
                   LogicArray("00110000011100"), \
                   LogicArray("00110000111000"), \
                   LogicArray("00110111110000"), \
                   LogicArray("00111111000000"), \
                   LogicArray("00001100000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 0

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((60, 7))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=59, Sample=22, Expected BCD=9
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 9

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((59, 22))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=142, Sample=56, Expected BCD=9
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000001000000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001110110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 9

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((142, 56))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=93, Sample=49, Expected BCD=8
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001110111000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 8

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((93, 49))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=60, Sample=20, Expected BCD=5
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00001100000000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00000001111100"), \
                   LogicArray("00001100011100"), \
                   LogicArray("00001111111100"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 5

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((60, 20))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=131, Sample=48, Expected BCD=1
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 1

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((131, 48))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=123, Sample=41, Expected BCD=0
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000010000"), \
                   LogicArray("00000011111000"), \
                   LogicArray("00000111111100"), \
                   LogicArray("00001111111110"), \
                   LogicArray("00011111111110"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00111110111100"), \
                   LogicArray("00111101111100"), \
                   LogicArray("00111111111000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 0

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((123, 41))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=128, Sample=6, Expected BCD=2
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00111111111110"), \
                   LogicArray("00011000111100"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 2

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((128, 6))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=123, Sample=2, Expected BCD=9
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000011111100"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00001111011100"), \
                   LogicArray("00011100111100"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00000100000000"), \
    ]

    classification_result = 9

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((123, 2))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=84, Sample=46, Expected BCD=7
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00111111111000"), \
                   LogicArray("00111111111000"), \
                   LogicArray("00111111011000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000111000000"), \
    ]

    classification_result = 7

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((84, 46))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=7, Sample=31, Expected BCD=9
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00011101110000"), \
                   LogicArray("00011000110000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000000011000"), \
                   LogicArray("00000110111000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 9

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((7, 31))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=143, Sample=13, Expected BCD=9
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000100000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 9

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((143, 13))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=60, Sample=14, Expected BCD=7
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("11111111110000"), \
                   LogicArray("01111111111000"), \
                   LogicArray("01100011111000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000000111100"), \
                   LogicArray("00000000111100"), \
                   LogicArray("00000000011000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 7

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((60, 14))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=113, Sample=8, Expected BCD=5
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000011110"), \
                   LogicArray("00000111111100"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00111111100000"), \
                   LogicArray("00111111000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 5

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((113, 8))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=89, Sample=62, Expected BCD=4
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000001100"), \
                   LogicArray("00001110001100"), \
                   LogicArray("00001110011100"), \
                   LogicArray("00001100011100"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 4

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((89, 62))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=82, Sample=43, Expected BCD=1
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 1

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((82, 43))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=75, Sample=11, Expected BCD=7
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00111111111000"), \
                   LogicArray("00111110111000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011000000"), \
    ]

    classification_result = 7

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((75, 11))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=91, Sample=30, Expected BCD=7
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00011100111000"), \
                   LogicArray("00111100110000"), \
                   LogicArray("00111001110000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 7

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((91, 30))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=141, Sample=38, Expected BCD=2
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00111001110000"), \
                   LogicArray("00011001110000"), \
                   LogicArray("00011011110000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000111111110"), \
                   LogicArray("00000111111110"), \
                   LogicArray("00000111111110"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 2

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((141, 38))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=23, Sample=58, Expected BCD=8
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00001000000000"), \
                   LogicArray("00111111111000"), \
                   LogicArray("00111111111000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00000111111100"), \
                   LogicArray("00000011111000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000010000000"), \
    ]

    classification_result = 8

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((23, 58))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=31, Sample=23, Expected BCD=4
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00011000110000"), \
                   LogicArray("00011001110000"), \
                   LogicArray("00011001110000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00011101100000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 4

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((31, 23))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=105, Sample=15, Expected BCD=8
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000011"), \
                   LogicArray("00000111111111"), \
                   LogicArray("00000111111110"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00011111000000"), \
                   LogicArray("00011111000000"), \
                   LogicArray("00011111000000"), \
                   LogicArray("00001100000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 8

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((105, 15))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=43, Sample=6, Expected BCD=8
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00011100011100"), \
                   LogicArray("00011100011100"), \
                   LogicArray("00001111111100"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 8

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((43, 6))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=121, Sample=43, Expected BCD=6
    # --------------------------------------------
    input_image = [LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00011111111110"), \
                   LogicArray("00011111111110"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 6

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((121, 43))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=151, Sample=38, Expected BCD=5
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000001110"), \
                   LogicArray("00000111111110"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00011110000000"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00010111100000"), \
                   LogicArray("00011111000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 5

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((151, 38))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=17, Sample=8, Expected BCD=7
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00011100011100"), \
                   LogicArray("00011100011100"), \
                   LogicArray("00011100111000"), \
                   LogicArray("00011100111000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011000000"), \
    ]

    classification_result = 7

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((17, 8))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=116, Sample=23, Expected BCD=1
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000001110"), \
                   LogicArray("00000000011100"), \
                   LogicArray("00000000011100"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00011100000000"), \
                   LogicArray("00111000000000"), \
                   LogicArray("00010000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 1

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((116, 23))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=98, Sample=8, Expected BCD=0
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000100000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00001110111100"), \
                   LogicArray("00001110011100"), \
                   LogicArray("00011100011100"), \
                   LogicArray("00011100011100"), \
                   LogicArray("00011000011000"), \
                   LogicArray("00011100111000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 0

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((98, 8))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=17, Sample=27, Expected BCD=5
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001100000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 5

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((17, 27))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=111, Sample=5, Expected BCD=8
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00010001110000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 8

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((111, 5))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=123, Sample=32, Expected BCD=6
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000011111000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00111111111110"), \
                   LogicArray("00111111111110"), \
                   LogicArray("00111111111100"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 6

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((123, 32))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=66, Sample=37, Expected BCD=5
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00001100000000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00011110001100"), \
                   LogicArray("00001000001100"), \
                   LogicArray("00000000111100"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 5

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((66, 37))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=81, Sample=16, Expected BCD=4
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000100000000"), \
                   LogicArray("00001100110000"), \
                   LogicArray("00001100110000"), \
                   LogicArray("00011101110000"), \
                   LogicArray("00011101110000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 4

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((81, 16))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=7, Sample=57, Expected BCD=3
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001000111000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000101110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 3

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((7, 57))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=8, Sample=45, Expected BCD=7
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00111111110000"), \
                   LogicArray("00111111110000"), \
                   LogicArray("00010001110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 7

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((8, 45))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=59, Sample=59, Expected BCD=6
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00010000000000"), \
                   LogicArray("00011000000000"), \
                   LogicArray("00111000000000"), \
                   LogicArray("00111000111100"), \
                   LogicArray("00111001111110"), \
                   LogicArray("00111011111110"), \
                   LogicArray("00111011101110"), \
                   LogicArray("00111011101110"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 6

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((59, 59))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=34, Sample=7, Expected BCD=4
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00001110001100"), \
                   LogicArray("00001110001110"), \
                   LogicArray("00011100011100"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00111111111100"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 4

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((34, 7))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=23, Sample=43, Expected BCD=1
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 1

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((23, 43))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=28, Sample=51, Expected BCD=0
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00001100111000"), \
                   LogicArray("00001100111000"), \
                   LogicArray("00011100111000"), \
                   LogicArray("00011100111000"), \
                   LogicArray("00011101111000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 0

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((28, 51))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=119, Sample=38, Expected BCD=7
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000110000000"), \
    ]

    classification_result = 7

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((119, 38))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=90, Sample=1, Expected BCD=2
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000111111100"), \
                   LogicArray("00001111101100"), \
                   LogicArray("00001111001110"), \
                   LogicArray("00000000001100"), \
                   LogicArray("00000000011100"), \
                   LogicArray("00000000011100"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00111111111000"), \
                   LogicArray("01111111010000"), \
                   LogicArray("00111100000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 2

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((90, 1))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=103, Sample=44, Expected BCD=3
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00000111111100"), \
                   LogicArray("00001111011100"), \
                   LogicArray("00011100011100"), \
                   LogicArray("00011000111000"), \
                   LogicArray("00010001110000"), \
                   LogicArray("00111111100000"), \
                   LogicArray("00011111000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 3

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((103, 44))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=113, Sample=29, Expected BCD=0
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000001000"), \
                   LogicArray("00000001111100"), \
                   LogicArray("00000011111100"), \
                   LogicArray("00000111111100"), \
                   LogicArray("00001111001100"), \
                   LogicArray("00011110001100"), \
                   LogicArray("00011100011100"), \
                   LogicArray("00111000111000"), \
                   LogicArray("00110111111000"), \
                   LogicArray("00111111110000"), \
                   LogicArray("00111111000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 0

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((113, 29))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=63, Sample=54, Expected BCD=8
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00011110000000"), \
                   LogicArray("00111111100000"), \
                   LogicArray("00111111100000"), \
                   LogicArray("00111111111100"), \
                   LogicArray("00111111111100"), \
                   LogicArray("00001111111100"), \
                   LogicArray("00001111111100"), \
                   LogicArray("00001111111100"), \
                   LogicArray("00000111111100"), \
                   LogicArray("00000011111100"), \
                   LogicArray("00000001111000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 8

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((63, 54))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=12, Sample=3, Expected BCD=7
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000010000000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00011001110000"), \
                   LogicArray("00011001110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 7

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((12, 3))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=40, Sample=26, Expected BCD=5
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011111000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 5

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((40, 26))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=31, Sample=44, Expected BCD=7
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000011100"), \
                   LogicArray("00000111111100"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00011101110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00001100000000"), \
                   LogicArray("00001100000000"), \
                   LogicArray("00001100000000"), \
                   LogicArray("00001100000000"), \
    ]

    classification_result = 7

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((31, 44))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=24, Sample=60, Expected BCD=9
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00001101110000"), \
                   LogicArray("00011001110000"), \
                   LogicArray("00011001110000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 9

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((24, 60))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=90, Sample=50, Expected BCD=6
    # --------------------------------------------
    input_image = [LogicArray("00000000110000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 6

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((90, 50))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=109, Sample=60, Expected BCD=5
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000111110"), \
                   LogicArray("00000111111110"), \
                   LogicArray("00000111111100"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00011100111000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 5

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((109, 60))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=89, Sample=63, Expected BCD=1
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011001100"), \
                   LogicArray("00000111000100"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00001110000100"), \
                   LogicArray("00001100000100"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 1

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((89, 63))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=152, Sample=5, Expected BCD=9
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000001111110"), \
                   LogicArray("00000111111110"), \
                   LogicArray("00001110111100"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00011100000000"), \
                   LogicArray("00011000000000"), \
    ]

    classification_result = 9

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((152, 5))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=86, Sample=56, Expected BCD=7
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001110111000"), \
                   LogicArray("00001110111000"), \
                   LogicArray("00011101110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011000000"), \
    ]

    classification_result = 7

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((86, 56))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=129, Sample=39, Expected BCD=2
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000011111110"), \
                   LogicArray("00001111111110"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00111111100000"), \
                   LogicArray("00111110000000"), \
                   LogicArray("00111100000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 2

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((129, 39))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=86, Sample=24, Expected BCD=5
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011111000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001110111000"), \
                   LogicArray("00001100111000"), \
                   LogicArray("00011100111000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 5

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((86, 24))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=110, Sample=11, Expected BCD=6
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000011000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000111111100"), \
                   LogicArray("00001111111100"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00111111110000"), \
                   LogicArray("00111111100000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 6

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((110, 11))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=13, Sample=37, Expected BCD=5
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000111100"), \
                   LogicArray("00011111111110"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000011000000"), \
    ]

    classification_result = 5

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((13, 37))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=142, Sample=49, Expected BCD=0
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00011100111100"), \
                   LogicArray("00011100011110"), \
                   LogicArray("00111000011100"), \
                   LogicArray("00111001111100"), \
                   LogicArray("00111111111000"), \
                   LogicArray("00111111110000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 0

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((142, 49))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=39, Sample=5, Expected BCD=3
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000001000000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000001111000"), \
                   LogicArray("00111111110000"), \
                   LogicArray("00111111000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 3

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((39, 5))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=109, Sample=25, Expected BCD=2
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000100000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00011111011000"), \
                   LogicArray("00011110000000"), \
                   LogicArray("00011100000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 2

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((109, 25))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=149, Sample=47, Expected BCD=5
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000011100"), \
                   LogicArray("00000011111110"), \
                   LogicArray("00001111111110"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00111111100000"), \
                   LogicArray("00111111100000"), \
                   LogicArray("00001100000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 5

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((149, 47))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=71, Sample=59, Expected BCD=1
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
                   LogicArray("00000011100000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 1

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((71, 59))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=14, Sample=10, Expected BCD=9
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
    ]

    classification_result = 9

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((14, 10))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=0, Sample=62, Expected BCD=9
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001101110000"), \
                   LogicArray("00001100000000"), \
                   LogicArray("00001100100000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 9

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((0, 62))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=34, Sample=51, Expected BCD=9
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00001100110000"), \
                   LogicArray("00011000110000"), \
                   LogicArray("00011001110000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00000110110000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000000110000"), \
    ]

    classification_result = 9

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((34, 51))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=137, Sample=17, Expected BCD=3
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000001111000"), \
                   LogicArray("00110001110000"), \
                   LogicArray("00111111110000"), \
                   LogicArray("00111111100000"), \
                   LogicArray("00011111000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 3

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((137, 17))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=16, Sample=55, Expected BCD=6
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00001111111100"), \
                   LogicArray("00001101111100"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00011011111000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 6

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((16, 55))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=128, Sample=0, Expected BCD=5
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000001111000"), \
                   LogicArray("00000111111110"), \
                   LogicArray("00001111011100"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00011111000000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00010001111000"), \
                   LogicArray("00111111110000"), \
                   LogicArray("00111111100000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 5

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((128, 0))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=112, Sample=43, Expected BCD=3
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00000011111000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000110110000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("01100001110000"), \
                   LogicArray("01111111110000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 3

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((112, 43))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=14, Sample=28, Expected BCD=2
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00001111111100"), \
                   LogicArray("01111111111100"), \
                   LogicArray("01111000011100"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00011111000000"), \
                   LogicArray("00011110000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 2

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((14, 28))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=120, Sample=20, Expected BCD=9
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000100000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001100110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 9

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((120, 20))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=34, Sample=16, Expected BCD=5
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000010000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00011000011000"), \
                   LogicArray("00011000011000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00000010000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 5

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((34, 16))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=96, Sample=38, Expected BCD=1
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000010000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 1

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((96, 38))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=136, Sample=19, Expected BCD=9
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000001000000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001100110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 9

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((136, 19))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=57, Sample=3, Expected BCD=1
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
                   LogicArray("00000011100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 1

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((57, 3))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=128, Sample=20, Expected BCD=0
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000011000"), \
                   LogicArray("00000000111100"), \
                   LogicArray("00001110011100"), \
                   LogicArray("00011110001110"), \
                   LogicArray("00111000001110"), \
                   LogicArray("00111000011100"), \
                   LogicArray("01110000111100"), \
                   LogicArray("00111111110000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 0

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((128, 20))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=120, Sample=43, Expected BCD=0
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001110111000"), \
                   LogicArray("00011100011100"), \
                   LogicArray("00011100011110"), \
                   LogicArray("00111000001110"), \
                   LogicArray("00111000001110"), \
                   LogicArray("00111000001110"), \
                   LogicArray("00111111111100"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 0

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((120, 43))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=34, Sample=42, Expected BCD=4
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00001110110000"), \
                   LogicArray("00001100110000"), \
                   LogicArray("00001101110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 4

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((34, 42))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=3, Sample=14, Expected BCD=9
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000001111000"), \
                   LogicArray("00000000110000"), \
    ]

    classification_result = 9

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((3, 14))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=131, Sample=61, Expected BCD=5
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111111111"), \
                   LogicArray("00001111111110"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 5

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((131, 61))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=53, Sample=61, Expected BCD=7
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 7

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((53, 61))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=20, Sample=45, Expected BCD=8
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000011000"), \
                   LogicArray("00000001111100"), \
                   LogicArray("00000011111100"), \
                   LogicArray("00001111011100"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00111101110000"), \
                   LogicArray("00111111100000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 8

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((20, 45))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=151, Sample=24, Expected BCD=0
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000011000"), \
                   LogicArray("00000011111000"), \
                   LogicArray("00000011111100"), \
                   LogicArray("00000111101110"), \
                   LogicArray("00001111001100"), \
                   LogicArray("00001110011100"), \
                   LogicArray("00011100111000"), \
                   LogicArray("00111101110000"), \
                   LogicArray("00111111000000"), \
                   LogicArray("00011110000000"), \
                   LogicArray("00001100000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 0

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((151, 24))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=149, Sample=21, Expected BCD=8
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011110100"), \
                   LogicArray("00000011111110"), \
                   LogicArray("00000111111100"), \
                   LogicArray("00000111111100"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00011111000000"), \
                   LogicArray("00011111000000"), \
                   LogicArray("00011110000000"), \
                   LogicArray("00011100000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 8

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((149, 21))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=107, Sample=55, Expected BCD=9
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000011000000"), \
    ]

    classification_result = 9

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((107, 55))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=29, Sample=62, Expected BCD=0
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000100000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00001110111000"), \
                   LogicArray("00001100111000"), \
                   LogicArray("00011100111000"), \
                   LogicArray("00011101110000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 0

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((29, 62))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=2, Sample=28, Expected BCD=6
    # --------------------------------------------
    input_image = [LogicArray("00000100000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00001100000000"), \
                   LogicArray("00001100000000"), \
                   LogicArray("00001100000000"), \
                   LogicArray("00001100000000"), \
                   LogicArray("00001100011100"), \
                   LogicArray("00001101111100"), \
                   LogicArray("00001111111100"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 6

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((2, 28))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=144, Sample=4, Expected BCD=0
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00001111111100"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00111100001100"), \
                   LogicArray("00111000001110"), \
                   LogicArray("00111000011100"), \
                   LogicArray("01111000111100"), \
                   LogicArray("00111111111000"), \
                   LogicArray("00111111110000"), \
                   LogicArray("00000100000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 0

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((144, 4))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=58, Sample=37, Expected BCD=6
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00001000000000"), \
                   LogicArray("00011000000000"), \
                   LogicArray("00011000011000"), \
                   LogicArray("00011000111100"), \
                   LogicArray("00111000111100"), \
                   LogicArray("00011000111100"), \
                   LogicArray("00011000111100"), \
                   LogicArray("00011101111100"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 6

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((58, 37))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=40, Sample=24, Expected BCD=8
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000010000"), \
                   LogicArray("00000001111000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00011100110000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 8

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((40, 24))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=80, Sample=38, Expected BCD=3
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("01100001111000"), \
                   LogicArray("01111111110000"), \
                   LogicArray("01111111100000"), \
                   LogicArray("00001100000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 3

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((80, 38))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=54, Sample=44, Expected BCD=4
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00010000010000"), \
                   LogicArray("00011000111000"), \
                   LogicArray("00111000111000"), \
                   LogicArray("00111000111000"), \
                   LogicArray("00111100111000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000000011000"), \
                   LogicArray("00000000011000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 4

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((54, 44))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=107, Sample=23, Expected BCD=7
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00111111110000"), \
                   LogicArray("00011000110000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000001100000"), \
    ]

    classification_result = 7

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((107, 23))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=115, Sample=22, Expected BCD=9
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000001000000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 9

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((115, 22))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=62, Sample=61, Expected BCD=4
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00001110010000"), \
                   LogicArray("00001110110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000001000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 4

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((62, 61))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=14, Sample=27, Expected BCD=3
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00111111111000"), \
                   LogicArray("01111111111000"), \
                   LogicArray("00110011111000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000001111000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 3

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((14, 27))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=125, Sample=22, Expected BCD=1
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001111000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00000100000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 1

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((125, 22))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=22, Sample=51, Expected BCD=2
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00111100000000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000101110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00111111111000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 2

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((22, 51))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=142, Sample=42, Expected BCD=6
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00011100111000"), \
                   LogicArray("00011101111100"), \
                   LogicArray("00011011111100"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 6

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((142, 42))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=45, Sample=21, Expected BCD=4
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 4

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((45, 21))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=128, Sample=45, Expected BCD=6
    # --------------------------------------------
    input_image = [LogicArray("00000000001000"), \
                   LogicArray("00000000111100"), \
                   LogicArray("00000011111000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00011111011100"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 6

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((128, 45))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=45, Sample=59, Expected BCD=9
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00111110111000"), \
                   LogicArray("00111100011000"), \
                   LogicArray("00011000011100"), \
                   LogicArray("00000000011100"), \
                   LogicArray("00000000011000"), \
                   LogicArray("00000001111000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 9

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((45, 59))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=64, Sample=5, Expected BCD=9
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000001000000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000001000000"), \
    ]

    classification_result = 9

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((64, 5))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=7, Sample=35, Expected BCD=5
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111011111"), \
                   LogicArray("00001111111111"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00001100000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00001100000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 5

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((7, 35))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=68, Sample=13, Expected BCD=0
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00001110111000"), \
                   LogicArray("00011100011000"), \
                   LogicArray("00011100011000"), \
                   LogicArray("00011000111000"), \
                   LogicArray("00011000111000"), \
                   LogicArray("00011101110000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 0

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((68, 13))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=18, Sample=47, Expected BCD=6
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00011110011000"), \
                   LogicArray("00011111011100"), \
                   LogicArray("00001111111100"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000000100000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 6

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((18, 47))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=143, Sample=17, Expected BCD=7
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00011001111000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00111111111000"), \
                   LogicArray("00011101111000"), \
                   LogicArray("00011101111000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000001100000"), \
    ]

    classification_result = 7

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((143, 17))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=155, Sample=1, Expected BCD=6
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00001110010000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00011111111100"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00111111111000"), \
                   LogicArray("00111111100000"), \
                   LogicArray("00001000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 6

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((155, 1))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=61, Sample=14, Expected BCD=5
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011111000"), \
                   LogicArray("00001111111110"), \
                   LogicArray("00011110000110"), \
                   LogicArray("00011000000010"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00011111000000"), \
                   LogicArray("00011100000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 5

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((61, 14))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=103, Sample=0, Expected BCD=9
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000110111000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001110110000"), \
                   LogicArray("00000101100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 9

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((103, 0))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=140, Sample=37, Expected BCD=6
    # --------------------------------------------
    input_image = [LogicArray("00000000010000"), \
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

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((140, 37))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=37, Sample=54, Expected BCD=6
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00001100000000"), \
                   LogicArray("00001100000000"), \
                   LogicArray("00001100111000"), \
                   LogicArray("00001101111000"), \
                   LogicArray("00001001111000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 6

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((37, 54))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=74, Sample=12, Expected BCD=8
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00011111111000"), \
                   LogicArray("00111111111100"), \
                   LogicArray("00111100011100"), \
                   LogicArray("00001110111100"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000011000000"), \
    ]

    classification_result = 8

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((74, 12))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=136, Sample=0, Expected BCD=2
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00011101110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00000001110000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00011111111110"), \
                   LogicArray("00011111111110"), \
                   LogicArray("00011110001100"), \
                   LogicArray("00001000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 2

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((136, 0))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=117, Sample=43, Expected BCD=5
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011111110"), \
                   LogicArray("00000111111100"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00111011110000"), \
                   LogicArray("00111111100000"), \
                   LogicArray("00011111000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 5

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((117, 43))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=62, Sample=6, Expected BCD=1
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
                   LogicArray("00000010000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 1

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((62, 6))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=9, Sample=3, Expected BCD=7
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00000111111000"), \
                   LogicArray("00001100111000"), \
                   LogicArray("00001101110000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00001110000000"), \
                   LogicArray("00000110000000"), \
    ]

    classification_result = 7

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((9, 3))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=49, Sample=48, Expected BCD=7
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00011110000000"), \
                   LogicArray("00011111100000"), \
                   LogicArray("00011111110000"), \
                   LogicArray("00000000110000"), \
                   LogicArray("00000001111000"), \
                   LogicArray("00000011111000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
                   LogicArray("00000001100000"), \
    ]

    classification_result = 7

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((49, 48))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=49, Sample=53, Expected BCD=7
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("01111111111000"), \
                   LogicArray("01111111111000"), \
                   LogicArray("00000001111000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000010000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 7

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((49, 53))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=28, Sample=26, Expected BCD=6
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00001111000000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 6

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((28, 26))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=84, Sample=53, Expected BCD=9
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011110000"), \
                   LogicArray("00000111110000"), \
                   LogicArray("00001111111000"), \
                   LogicArray("00001101111000"), \
                   LogicArray("00001111110000"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000011100000"), \
                   LogicArray("00000011000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000110000000"), \
                   LogicArray("00000110000000"), \
    ]

    classification_result = 9

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((84, 53))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=99, Sample=32, Expected BCD=5
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000011111110"), \
                   LogicArray("00000111111110"), \
                   LogicArray("00000111100000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00000111000000"), \
                   LogicArray("00100001100000"), \
                   LogicArray("00111101100000"), \
                   LogicArray("00111111100000"), \
                   LogicArray("00011111000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
    ]

    classification_result = 5

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((99, 32))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # Subtest: Batch=32, Sample=0, Expected BCD=7
    # --------------------------------------------
    input_image = [LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00000000000000"), \
                   LogicArray("00111111110000"), \
                   LogicArray("01111111111000"), \
                   LogicArray("01111111111000"), \
                   LogicArray("00111111111000"), \
                   LogicArray("00010001111000"), \
                   LogicArray("00000001111000"), \
                   LogicArray("00000001111000"), \
                   LogicArray("00000001111000"), \
                   LogicArray("00000000111000"), \
                   LogicArray("00000000111100"), \
                   LogicArray("00000000011000"), \
    ]

    classification_result = 7

    subtests_tried += 1
    subtest_passed = True

    # Enter 'READ' Mode
    dut.ui_in.value = 0                       # Negative Edge (start transmission)
    await ClockCycles(dut.clk, 2)
    if int(dut.uo_out[7].value) != 0:         # Confirm Outputs Invalid (flag = 0) before Image is Transmitted
        subtest_passed = False

    # Transmit Input Image (Serial Transmission)
    dut._log.info('Transmitting Image...')
    for img_row in input_image:
        dut.ui_in.value = 128 + img_row[13:7].integer
        await ClockCycles(dut.clk, 1)
        dut.ui_in.value = 128 + img_row[6:0].integer
        await ClockCycles(dut.clk, 1)
    dut._log.info('Transmitting Image...Done')

    # Wait for Additional Clock Cycle(s) Before Evaluating
    await ClockCycles(dut.clk, 10)

    # Evaluate Results
    dut._log.info('Evaluating...')
    if int(dut.uo_out[7].value) != 1:  #Test Classification Flag set to 1
        subtest_passed = False
    if int(dut.uio_oe.value) != 0xFF:  #Test All Bidirectional I/O Output Enable set to '1'
        subtest_passed = False
    if int(dut.uio_out.value) != classification_result:
        subtest_passed = False
    if('1.8.1' in cocotb.__version__):
        # Flip Endian-ness in cocotb v1.8.1
        if int(dut.uo_out.value[1:7]) != segments[classification_result]:
            subtest_passed = False
    else:
        if int(dut.uo_out.value[6:0]) != segments[classification_result]:
            subtest_passed = False
    dut._log.info('Evaluating...Done')

    if subtest_passed:
        subtests_passed += 1
    else:
        failed_subtests.append((32, 0))

    # Reset DUT before next subtest
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # --------------------------------------------
    # AGGREGATE PASS / FAIL CRITERIA
    # --------------------------------------------
    pass_rate = subtests_passed / subtests_tried if subtests_tried > 0 else 0
    dut._log.info(f'Subtests Passed: {subtests_passed}/{subtests_tried} ({pass_rate:.2%})')
    if failed_subtests:
        dut._log.info(f'Failed Subtests (batch, sample): {failed_subtests}')
    assert pass_rate >= THRESHOLD, f'Pass rate {pass_rate:.2%} below threshold {THRESHOLD:.2%}'


