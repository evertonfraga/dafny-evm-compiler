const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("MappingChecker (Dafny 'in' operator)", function () {
  let contract;
  let owner;
  let addr1;

  beforeEach(async function () {
    [owner, addr1] = await ethers.getSigners();
    
    const artifact = require("../contracts-out/MappingChecker.json");
    const factory = new ethers.ContractFactory(artifact.abi, artifact.bytecode, owner);
    contract = await factory.deploy();
    await contract.deployed();
  });

  describe("hasBalance", function () {
    it("Should return false for address with no balance", async function () {
      const exists = await contract.hasBalance(addr1.address);
      expect(exists).to.equal(false);
    });

    it("Should return true after setting balance", async function () {
      await contract.setBalance(addr1.address, 100);
      const exists = await contract.hasBalance(addr1.address);
      expect(exists).to.equal(true);
    });
  });

  describe("checkAndGet", function () {
    it("Should return false and 0 for non-existent address", async function () {
      const [has, value] = await contract.checkAndGet(addr1.address);
      expect(has).to.equal(false);
      expect(value.toNumber()).to.equal(0);
    });

    it("Should return true and value for existing address", async function () {
      await contract.setBalance(addr1.address, 500);
      const [has, value] = await contract.checkAndGet(addr1.address);
      expect(has).to.equal(true);
      expect(value.toNumber()).to.equal(500);
    });
  });
});
