Blockly.Blocks['1752580122938'] = {
  init: function() {
    this.jsonInit({
      "type": "1752580122938",
      "message0": "爹块小右走1",
      "previousStatement": "motion_block",
      "nextStatement": "motion_block",
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1752580122938'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(30)\nMOTOmove19(66,21,190,100,113,70,123,98,129,174,10,99,87,132,76,104,120,40,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(66,21,190,95,114,69,122,100,129,174,10,120,79,122,77,111,120,40,100)\nMOTOwait()\nMOTOsetspeed(50)\nMOTOmove19(66,21,190,100,113,70,123,98,129,174,10,99,87,132,76,104,120,40,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1752580122938'] = function(block) {
  let code = "robot.leju_action('爹块小右走1')\n";
  return code;
}

