-- ===================================================================
-- 1. ZÁKLADNÍ NASTAVENÍ NEOVIMU
-- ===================================================================
vim.o.termguicolors = true   -- Povolí 24-bit barvy
vim.o.number = true          -- Ukazuje čísla řádků
vim.o.relativenumber = true  -- Ukazuje relativní čísla řádků
vim.o.mouse = 'a'            -- Povolí myš
vim.o.clipboard = 'unnamedplus' -- Sdílí schránku se systémem
vim.o.signcolumn = 'yes'     -- Vždy ukazuj sloupec pro chyby (důležité pro CoC)
vim.o.updatetime = 300       -- Rychlejší odezva (pro CoC)
vim.o.backup = false         -- Nevytvářej zálohy
vim.o.writebackup = false    -- Nevytvářej zálohy
vim.o.ts = 2                 -- Tabulátor na 2 mezery
vim.o.sts = 2                -- Shift-tabulátor na 2 mezery
vim.o.sw = 2                 -- Odsazení na 2 mezery
vim.o.expandtab = true       -- Převáděj tabulátory na mezery

-- ===================================================================
-- 2. INSTALACE SPRÁVCE PLUGINŮ (LAZY.NVIM)
-- ===================================================================
local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
if not vim.loop.fs_stat(lazypath) then
  vim.fn.system({
    "git",
    "clone",
    "--filter=blob:none",
    "https://github.com/folke/lazy.nvim.git",
    "--branch=stable",
    lazypath,
  })
end
vim.opt.rtp:prepend(lazypath)

-- ===================================================================
-- 3. SEZNAM A NASTAVENÍ PLUGINŮ
-- ===================================================================
-- ===================================================================
-- 3. SEZNAM A NASTAVENÍ PLUGINŮ (MODERNÍ VERZE)
-- ===================================================================
require("lazy").setup({

  -- Téma (které už máš)
  {
    "ianklapouch/wildberries.nvim",
    priority = 1000, -- Musí se načíst jako první
    config = function()
      vim.cmd.colorscheme "wildberries"
    end,
  },

  -- Status lišta (kterou už máš)
  {
    'nvim-lualine/lualine.nvim',
    dependencies = { 'nvim-tree/nvim-web-devicons' },
    config = function()
      require('lualine').setup({
        options = {
          theme = 'auto'
        }
      })
    end,
  },
  { 'nvim-tree/nvim-web-devicons', lazy = true },


  -- ===================================================================
  -- NOVÉ: NAŠEPTÁVÁNÍ (NÁHRADA ZA COC.NVIM)
  -- ===================================================================

  -- 1. "Mozek" - Správce LSP serverů
  { 'williamboman/mason.nvim', config = true },
  { 'williamboman/mason-lspconfig.nvim' },
  { 'neovim/nvim-lspconfig' },

  -- 2. "Našeptávač" (Completion Engine) - NÁHRADA ZA COC
  { 'hrsh7th/nvim-cmp' },

  -- 3. Zdroje pro našeptávač
  { 'hrsh7th/cmp-nvim-lsp' }, -- Zdroj z LSP (to chceme pro C++/Python)
  { 'hrsh7th/cmp-buffer' },  -- Zdroj z otevřených souborů
  { 'hrsh7th/cmp-path' },    -- Zdroj z cest v systému

  -- 4. Vizuální doplňky pro menu (volitelné, ale hezké)
  { 'onsails/lspkind.nvim' },

}) -- Konec lazy.setup


-- ===================================================================
-- 4. KONFIGURACE PRO NAŠEPTÁVÁNÍ (LSP A CMP)
-- ===================================================================

-- ------
-- Konfigurace pro nvim-cmp (to je to menu)
-- ------
local cmp = require('cmp')
local lspkind = require('lspkind') -- Pro hezké ikonky v menu

cmp.setup({
  sources = cmp.config.sources({
    { name = 'nvim_lsp' }, -- Našeptávej z LSP
    { name = 'buffer' },   -- Našeptávej ze souboru
    { name = 'path' },     -- Našeptávej cesty
  }),

  -- Vizuální styl menu
  formatting = {
    format = lspkind.cmp_format({
      mode = 'symbol',
      maxwidth = 50,
    })
  },

  -- ZDE JE TO MAPOVÁNÍ KLÁVES, KTERÉ CHCEŠ
  mapping = cmp.mapping.preset.insert({
    -- Pohyb v menu
    ['<C-k>'] = cmp.mapping.select_prev_item(),
    ['<C-j>'] = cmp.mapping.select_next_item(),
    
    -- Potvrzení výběru pomocí ENTER
    ['<CR>'] = cmp.mapping.confirm({ select = true }), 

    -- Vyvolání našeptávání (Ctrl+Space)
    ['<C-Space>'] = cmp.mapping.complete(),
  }),
})


-- ------
-- Konfigurace pro LSP (to je ten mozek)
-- ------
local lspconfig = require('lspconfig')
local capabilities = require('cmp_nvim_lsp').default_capabilities() -- Řekne LSP, že má posílat data do 'cmp'

-- Zde řekneme 'mason', aby automaticky nastavil servery, které nainstalujeme
require('mason').setup()
require('mason-lspconfig').setup({
  ensure_installed = { "pyright", "clangd" }, -- Můžeš sem rovnou přidat servery
  handlers = {
    -- Výchozí handler (nastaví všechny servery za nás)
    function(server_name)
      lspconfig[server_name].setup({
        capabilities = capabilities,
      })
    end,
  },
})

-- Zapnutí podtrhávání chyb a diagnostiky
vim.diagnostic.config({
  virtual_text = true,
  signs = true,
  underline = true,
})
