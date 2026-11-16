Blockly.Blocks['1713952752586'] = {
  init: function() {
    this.jsonInit({
      "type": "1713952752586",
      "message0": "111",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1713952752586'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(30)\nMOTOmove19(80,30,100,100,93,55,124,100,120,170,100,100,107,145,76,100,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(122,164,190,100,93,55,124,100,96,17,10,100,107,145,76,100,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(122,164,190,97,91,55,121,67,96,17,10,104,99,130,87,91,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(122,164,190,106,110,150,36,105,96,17,10,104,99,130,87,91,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(122,164,190,102,160,37,190,104,96,17,10,104,99,130,87,91,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(122,164,190,102,160,37,190,104,96,17,10,100,82,50,154,81,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1713952752586'] = function(block) {
  let code = "robot.leju_action('111')\n";
  return code;
}

