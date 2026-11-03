Blockly.Blocks['1710684023060'] = {
  init: function() {
    this.jsonInit({
      "type": "1710684023060",
      "message0": "后退Pro",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1710684023060'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(20)\nMOTOmove19(80,30,100,104,111,70,120,112,120,170,100,103,79,120,73,108,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(80,30,100,95,120,73,145,97,120,170,100,96,137,114,122,99,128,71,100)\nMOTOwait()\nMOTOsetspeed(22)\nMOTOmove19(80,30,100,99,126,69,144,86,120,170,100,101,79,121,76,91,128,71,100)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(80,30,100,100,93,55,124,100,120,170,100,100,107,145,76,100,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1710684023060'] = function(block) {
  let code = "robot.leju_action('后退Pro')\n";
  return code;
}

