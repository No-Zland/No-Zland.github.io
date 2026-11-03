Blockly.Blocks['1751972714933'] = {
  init: function() {
    this.jsonInit({
      "type": "1751972714933",
      "message0": "box-down-max-2-4",
      "previousStatement": "motion_block",
      "nextStatement": "motion_block",
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1751972714933'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\n\n\n-- 1\nMOTOsetspeed(30)\nMOTOmove19(76,14,171,100,93,55,130,98,119,182,31,100,107,145,70,102,120,40,100)\nMOTOwait()\n\n\n-- 2\nMOTOsetspeed(20)\nMOTOmove19(74,20,142,100,93,55,124,100,121,186,57,100,107,145,76,100,128,71,100)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(74,20,142,99,101,150,38,97,121,186,57,100,97,50,164,99,128,71,100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(74,20,142,95,127,150,39,95,121,186,57,99,72,50,163,99,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(74,62,141,95,127,150,39,95,121,145,56,99,72,50,163,99,128,71,100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(74,58,141,97,113,120,76,99,118,143,58,99,86,79,123,100,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(80,30,100,100,93,55,124,100,120,170,100,100,107,145,76,100,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1751972714933'] = function(block) {
  let code = "robot.leju_action('box-down-max-2-4')\n";
  return code;
}

