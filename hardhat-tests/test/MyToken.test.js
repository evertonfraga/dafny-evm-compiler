const { expect } = require("chai");
const { ethers } = require("hardhat");
const fs = require("fs");
const path = require("path");

describe("MyToken", function () {
  let token;

  beforeEach(async function () {
    const artifact = JSON.parse(
      fs.readFileSync(path.resolve(__dirname, "../contracts-out/MyToken.json"), "utf8")
    );
    const factory = new ethers.ContractFactory(
      artifact.abi,
      artifact.bytecode,
      (await ethers.getSigners())[0]
    );
    token = await factory.deploy();
    await token.deployed();
  });

  it("Should deploy with initial supply", async function () {
    expect(token.address).to.match(/^0x[a-fA-F0-9]{40}$/);
  });

  it("Should mint tokens", async function () {
    await token.mint(1000);
    const balance = await token.balanceOf();
    expect(balance.toNumber()).to.equal(1000);
  });

  it("Should track total supply", async function () {
    await token.mint(500);
    await token.mint(300);
    const balance = await token.balanceOf();
    expect(balance.toNumber()).to.equal(800);
  });
});
