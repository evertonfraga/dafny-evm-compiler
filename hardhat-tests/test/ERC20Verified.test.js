const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("ERC20Verified (Fully Verified ERC20)", function () {
  let token;
  let owner;
  let addr1;
  let addr2;
  const INITIAL_SUPPLY = 1000000;

  beforeEach(async function () {
    [owner, addr1, addr2] = await ethers.getSigners();
    
    const artifact = require("../contracts-out/ERC20Verified.json");
    const factory = new ethers.ContractFactory(artifact.abi, artifact.bytecode, owner);
    token = await factory.deploy(INITIAL_SUPPLY);
    await token.deployed();
  });

  describe("Deployment", function () {
    it("Should set the right owner", async function () {
      expect(await token.getOwner()).to.equal(owner.address);
    });

    it("Should assign total supply to owner", async function () {
      const ownerBalance = await token.balanceOf(owner.address);
      expect(ownerBalance.toNumber()).to.equal(INITIAL_SUPPLY);
    });

    it("Should set correct total supply", async function () {
      expect((await token.getTotalSupply()).toNumber()).to.equal(INITIAL_SUPPLY);
    });

    it("Should not be paused initially", async function () {
      expect(await token.isPaused()).to.equal(false);
    });
  });

  describe("Transfer", function () {
    it("Should transfer tokens between accounts", async function () {
      await token.transfer(addr1.address, 100);
      expect((await token.balanceOf(addr1.address)).toNumber()).to.equal(100);
      expect((await token.balanceOf(owner.address)).toNumber()).to.equal(INITIAL_SUPPLY - 100);
    });

    it("Should fail if sender doesn't have enough tokens", async function () {
      const initialOwnerBalance = await token.balanceOf(owner.address);
      try {
        await token.connect(addr1).transfer(owner.address, 1);
        expect.fail("Should have reverted");
      } catch (error) {
        expect(error.message).to.include("revert");
      }
      expect((await token.balanceOf(owner.address)).toNumber()).to.equal(initialOwnerBalance.toNumber());
    });

    it("Should fail on zero amount", async function () {
      try {
        await token.transfer(addr1.address, 0);
        expect.fail("Should have reverted");
      } catch (error) {
        expect(error.message).to.include("revert");
      }
    });

    it("Should fail on zero address", async function () {
      try {
        await token.transfer(ethers.constants.AddressZero, 100);
        expect.fail("Should have reverted");
      } catch (error) {
        expect(error.message).to.include("revert");
      }
    });

    it("Should fail when paused", async function () {
      await token.pause();
      try {
        await token.transfer(addr1.address, 100);
        expect.fail("Should have reverted");
      } catch (error) {
        expect(error.message).to.include("revert");
      }
    });

    it("Should preserve total supply", async function () {
      const supplyBefore = await token.totalSupply();
      await token.transfer(addr1.address, 100);
      const supplyAfter = await token.totalSupply();
      expect(supplyAfter.toNumber()).to.equal(supplyBefore.toNumber());
    });
  });

  describe("Approve", function () {
    it("Should approve tokens for delegated transfer", async function () {
      await token.approve(addr1.address, 100);
      expect((await token.allowance(owner.address, addr1.address)).toNumber()).to.equal(100);
    });

    it("Should fail on zero spender address", async function () {
      try {
        await token.approve(ethers.constants.AddressZero, 100);
        expect.fail("Should have reverted");
      } catch (error) {
        expect(error.message).to.include("revert");
      }
    });

    it("Should fail when paused", async function () {
      await token.pause();
      try {
        await token.approve(addr1.address, 100);
        expect.fail("Should have reverted");
      } catch (error) {
        expect(error.message).to.include("revert");
      }
    });

    it("Should allow updating allowance", async function () {
      await token.approve(addr1.address, 100);
      await token.approve(addr1.address, 200);
      expect((await token.allowance(owner.address, addr1.address)).toNumber()).to.equal(200);
    });
  });

  describe("TransferFrom", function () {
    beforeEach(async function () {
      await token.approve(addr1.address, 100);
    });

    it("Should transfer tokens using allowance", async function () {
      await token.connect(addr1).transferFrom(owner.address, addr2.address, 50);
      expect((await token.balanceOf(addr2.address)).toNumber()).to.equal(50);
      expect((await token.balanceOf(owner.address)).toNumber()).to.equal(INITIAL_SUPPLY - 50);
    });

    it("Should decrease allowance after transfer", async function () {
      await token.connect(addr1).transferFrom(owner.address, addr2.address, 50);
      expect((await token.allowance(owner.address, addr1.address)).toNumber()).to.equal(50);
    });

    it("Should fail if allowance is insufficient", async function () {
      try {
        await token.connect(addr1).transferFrom(owner.address, addr2.address, 150);
        expect.fail("Should have reverted");
      } catch (error) {
        expect(error.message).to.include("revert");
      }
    });

    it("Should fail if balance is insufficient", async function () {
      await token.connect(owner).approve(addr1.address, INITIAL_SUPPLY + 1000);
      try {
        await token.connect(addr1).transferFrom(owner.address, addr2.address, INITIAL_SUPPLY + 1);
        expect.fail("Should have reverted");
      } catch (error) {
        expect(error.message).to.include("revert");
      }
    });

    it("Should fail on zero amount", async function () {
      try {
        await token.connect(addr1).transferFrom(owner.address, addr2.address, 0);
        expect.fail("Should have reverted");
      } catch (error) {
        expect(error.message).to.include("revert");
      }
    });

    it("Should fail on zero to address", async function () {
      try {
        await token.connect(addr1).transferFrom(owner.address, ethers.constants.AddressZero, 50);
        expect.fail("Should have reverted");
      } catch (error) {
        expect(error.message).to.include("revert");
      }
    });

    it("Should preserve total supply", async function () {
      const supplyBefore = await token.totalSupply();
      await token.connect(addr1).transferFrom(owner.address, addr2.address, 50);
      const supplyAfter = await token.totalSupply();
      expect(supplyAfter.toNumber()).to.equal(supplyBefore.toNumber());
    });
  });

  describe("Mint", function () {
    it("Should mint tokens to specified address", async function () {
      await token.mint(addr1.address, 500);
      expect((await token.balanceOf(addr1.address)).toNumber()).to.equal(500);
    });

    it("Should increase total supply", async function () {
      const supplyBefore = await token.totalSupply();
      await token.mint(addr1.address, 500);
      expect((await token.totalSupply()).toNumber()).to.equal(supplyBefore.toNumber() + 500);
    });

    it("Should fail if not owner", async function () {
      try {
        await token.connect(addr1).mint(addr2.address, 500);
        expect.fail("Should have reverted");
      } catch (error) {
        expect(error.message).to.include("revert");
      }
    });

    it("Should fail on zero amount", async function () {
      try {
        await token.mint(addr1.address, 0);
        expect.fail("Should have reverted");
      } catch (error) {
        expect(error.message).to.include("revert");
      }
    });

    it("Should fail when paused", async function () {
      await token.pause();
      try {
        await token.mint(addr1.address, 500);
        expect.fail("Should have reverted");
      } catch (error) {
        expect(error.message).to.include("revert");
      }
    });
  });

  describe("Burn", function () {
    it("Should burn tokens from specified address", async function () {
      await token.burn(owner.address, 500);
      expect((await token.balanceOf(owner.address)).toNumber()).to.equal(INITIAL_SUPPLY - 500);
    });

    it("Should decrease total supply", async function () {
      const supplyBefore = await token.totalSupply();
      await token.burn(owner.address, 500);
      expect((await token.totalSupply()).toNumber()).to.equal(supplyBefore.toNumber() - 500);
    });

    it("Should fail if not owner", async function () {
      try {
        await token.connect(addr1).burn(owner.address, 500);
        expect.fail("Should have reverted");
      } catch (error) {
        expect(error.message).to.include("revert");
      }
    });

    it("Should fail on zero amount", async function () {
      try {
        await token.burn(owner.address, 0);
        expect.fail("Should have reverted");
      } catch (error) {
        expect(error.message).to.include("revert");
      }
    });

    it("Should fail if balance insufficient", async function () {
      try {
        await token.burn(owner.address, INITIAL_SUPPLY + 1);
        expect.fail("Should have reverted");
      } catch (error) {
        expect(error.message).to.include("revert");
      }
    });

    it("Should fail when paused", async function () {
      await token.pause();
      try {
        await token.burn(owner.address, 500);
        expect.fail("Should have reverted");
      } catch (error) {
        expect(error.message).to.include("revert");
      }
    });
  });

  describe("Pause/Unpause", function () {
    it("Should pause the contract", async function () {
      await token.pause();
      expect(await token.isPaused()).to.equal(true);
    });

    it("Should unpause the contract", async function () {
      await token.pause();
      await token.unpause();
      expect(await token.isPaused()).to.equal(false);
    });

    it("Should fail pause if not owner", async function () {
      try {
        await token.connect(addr1).pause();
        expect.fail("Should have reverted");
      } catch (error) {
        expect(error.message).to.include("revert");
      }
    });

    it("Should fail unpause if not owner", async function () {
      await token.pause();
      try {
        await token.connect(addr1).unpause();
        expect.fail("Should have reverted");
      } catch (error) {
        expect(error.message).to.include("revert");
      }
    });

    it("Should fail pause if already paused", async function () {
      await token.pause();
      try {
        await token.pause();
        expect.fail("Should have reverted");
      } catch (error) {
        expect(error.message).to.include("revert");
      }
    });

    it("Should fail unpause if not paused", async function () {
      try {
        await token.unpause();
        expect.fail("Should have reverted");
      } catch (error) {
        expect(error.message).to.include("revert");
      }
    });
  });

  describe("View Functions", function () {
    it("Should return correct balance", async function () {
      await token.transfer(addr1.address, 100);
      expect((await token.balanceOf(addr1.address)).toNumber()).to.equal(100);
    });

    it("Should return correct allowance", async function () {
      await token.approve(addr1.address, 100);
      expect((await token.allowance(owner.address, addr1.address)).toNumber()).to.equal(100);
    });

    it("Should return correct total supply", async function () {
      expect((await token.totalSupply()).toNumber()).to.equal(INITIAL_SUPPLY);
    });

    it("Should return correct owner", async function () {
      expect(await token.owner()).to.equal(owner.address);
    });

    it("Should return correct pause status", async function () {
      expect(await token.isPaused()).to.equal(false);
      await token.pause();
      expect(await token.isPaused()).to.equal(true);
    });
  });
});
