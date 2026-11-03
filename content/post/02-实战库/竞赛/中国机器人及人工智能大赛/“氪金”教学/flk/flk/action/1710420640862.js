Blockly.Blocks['1710420640862'] = {
  init: function() {
    this.jsonInit({
      "type": "1710420640862",
      "message0": "放块ProMax",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1710420640862'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(60)\nMOTOmove19(72,10,167,53,154,150,59,62,127,190,36,140,40,50,137,140,128,71,100)\nMOTOwait()\nMOTOsetspeed(150)\nMOTOmove19(71,46,165,53,154,150,59,62,127,163,37,140,40,50,137,140,128,71,100)\nMOTOwait()\nMOTOsetspeed(33)\nMOTOmove19(80,30,100,100,93,55,124,100,120,170,100,100,107,145,76,100,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1710420640862'] = function(block) {
  let code = "robot.leju_action('放块ProMax')\n";
  return code;
}

