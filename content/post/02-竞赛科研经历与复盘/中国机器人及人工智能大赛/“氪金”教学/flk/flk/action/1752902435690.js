Blockly.Blocks['1752902435690'] = {
  init: function() {
    this.jsonInit({
      "type": "1752902435690",
      "message0": "1f2",
      "previousStatement": "motion_block",
      "nextStatement": "motion_block",
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1752902435690'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\n\n\n-- 2\nMOTOsetspeed(20)\nMOTOmove19(64,10,164,100,93,55,124,100,138,190,37,100,107,145,76,100,128,71,100)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(64,10,164,99,101,150,38,97,138,190,37,100,97,50,164,99,128,71,100)\nMOTOwait()\nMOTOsetspeed(5)\nMOTOmove19(64,10,164,95,127,150,39,95,138,190,37,99,72,50,163,99,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(74,62,141,95,127,150,39,95,121,145,56,99,72,50,163,99,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(73,62,64,95,110,150,44,96,121,144,136,98,83,50,152,98,128,71,100)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(80,30,100,100,93,55,124,100,120,170,100,100,107,145,76,100,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1752902435690'] = function(block) {
  let code = "robot.leju_action('1f2')\n";
  return code;
}

