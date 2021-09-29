// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./IERC20.sol";

contract ERC20 is IERC20{
    

    struct Hold {
        address executer;
        address sender;
        address recipient;
        uint256 balance;
        bool    declare;
    }

    mapping(address => uint256) private _balances;

    // Lo ideal sería una base de datos con sus claves únicas, 
    // debido a la embergadura del proyecto y el tiempo se decide realizar mpping
    mapping(uint256 => Hold) private _holds; 

    mapping(address => mapping(address => uint256)) private _allowances;

    uint256 private _totalSupply;

    string private _name;
    string private _symbol;

    
    constructor (string memory n, string memory s, uint256 initialSupply) {
        _name = n;
        _symbol = s;
        _totalSupply = initialSupply;
        _balances[tx.origin] = initialSupply;
    }

    /**
     * @dev Returns the name of the token.
     */
    function name() public view virtual returns (string memory) {
        return _name;
    }

    /**
     * @dev Returns the symbol of the token.
     */
    function symbol() public view virtual returns (string memory) {
        return _symbol;
    }

    /**
     * @dev See {IERC20-totalSupply}.
     */
    function totalSupply() public view virtual override returns (uint256) {
        return _totalSupply;
    }

    /**
     * @dev See {IERC20-balanceOf}.
     */
    function balanceOf(address account) public view virtual override returns (uint256){
        return _balances[account];
    }

    /**
     * @dev Returns if a hold exist or not.
     */
    function getHold(uint256 holdId) public view virtual returns (bool){
        return _holds[holdId].declare;
    }

    /**
     * @dev See {IERC20-transfer}.
     */
    function transfer(address recipient, uint256 amount) public virtual override returns (bool){
        _transfer(msg.sender, recipient, amount);
        return true;
    }

    /**
     * @dev See {IERC20-hold}.
     */
    function hold(address recipient, uint256 amount, uint256 holdId) public virtual override returns (bool){
        _hold(msg.sender, recipient, msg.sender, amount, holdId);
        return true;
    }

    /**
     * @dev See {IERC20-allowance}.
     */
    function allowance(address owner, address spender) public view virtual override returns (uint256){
        return _allowances[owner][spender];
    }

   /**
     * @dev See {IERC20-approve}.
     */
    function approve(address spender, uint256 amount) public virtual override returns (bool){
        _approve(msg.sender, spender, amount);
        return true;
    }

   /**
     * @dev See {IERC20-transferFrom}.
     */
    function transferFrom(address sender, address recipient, uint256 amount) public virtual override returns (bool){
        _transfer(sender, recipient, amount);

        uint256 current_allowances = _allowances[msg.sender][sender];
        require(current_allowances >= amount , "ERC20: transfer amount exceeds _allowances");
        unchecked {
            _approve(sender, msg.sender, current_allowances - amount);
        }

        return true;
    }

    /**
     * @dev See {IERC20-holdFrom}.
     */
    function holdFrom(address sender, address recipient, uint256 amount, uint256 holdId) public virtual override returns (bool){
        _hold(sender, recipient, msg.sender, amount, holdId);

        uint256 current_allowances = _allowances[msg.sender][sender];
        require(current_allowances >= amount , "ERC20: transfer amount exceeds _allowances");
        unchecked {
            _approve(sender, msg.sender, current_allowances - amount);
        }
        
        return true;
    }

    /**
     * @dev See {IERC20-executeHold}.
     */
    function executeHold(uint256 holdId) public virtual override returns (bool){
        require(_holds[holdId].declare                  , "ERC20: holdId doesnt exist");
        require(_holds[holdId].executer == msg.sender   , "ERC20: can only be executed by the same address that created the hold");

        _balances[_holds[holdId].recipient] += _holds[holdId].balance;

        emit Transfer(_holds[holdId].sender, _holds[holdId].recipient, _holds[holdId].balance);
        delete _holds[holdId];

        return true;
    }

    /**
     * @dev See {IERC20-removeHold}.
     */
    function removeHold(uint256 holdId) public virtual override returns (bool){
        require(_holds[holdId].declare                  , "ERC20: holdId doesnt exist");
        require(_holds[holdId].sender == msg.sender     , "ERC20: can only be called by the owner of the contract"); 

        _balances[_holds[holdId].sender] += _holds[holdId].balance;
        
        delete _holds[holdId];
        return true;
    }

    /**
     * @dev Moves `amount` of tokens from `sender` to `recipient`.
     */
    function _transfer(address sender, address recipient, uint256 amount) internal virtual {
        require(sender != address(0)        , "ERC20: transfer from the zero address");
        require(recipient != address(0)     , "ERC20: transfer to the zero address");
        require(_balances[sender] >= amount , "ERC20: sender doesnt have enough balance.");

        uint256 totalBalances = _balances[sender] + _balances[recipient];

        _balances[sender]    -= amount;
        _balances[recipient] += amount;

        emit Transfer(sender, recipient, amount);
        assert(_balances[sender] + _balances[recipient] == totalBalances );
    }

    /**
     * @dev Hold `amount` of tokens from `sender` to be transfered to `recipient` at another moment.
     */
    function _hold(address sender, address recipient, address executer, uint256 amount, uint256 holdId) internal virtual {
        require(sender != address(0)        , "ERC20: transfer from the zero address");
        require(recipient != address(0)     , "ERC20: transfer to the zero address");
        require(_balances[sender] >= amount , "ERC20: sender doesnt have enough balance.");
        require(!getHold(holdId)            , "ERC20: holdId already exist.");


        _holds[holdId].executer  = executer;
        _holds[holdId].sender    = sender;
        _holds[holdId].recipient = recipient;
        _holds[holdId].balance   = amount;
        _holds[holdId].declare   = true;
        

        _balances[sender] -= amount;
    }

    /**
     * @dev Sets `amount` as the allowance of `spender` over the `owner` s tokens.
     */
    function _approve(address owner, address spender, uint256 amount) internal virtual {
        require(owner != address(0)  , "ERC20: approve from the zero address");
        require(spender != address(0), "ERC20: approve to the zero address");

        _allowances[owner][spender] = amount;
        emit Approval(owner, spender, amount);
    }

}