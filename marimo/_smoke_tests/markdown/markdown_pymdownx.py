import marimo

_task_list_md = """
        ## Task List

        - item
        -   [X] item 1
            *   [X] item A
            *   [ ] item B
                more text
                +   [x] item a
                +   [ ] item b
                +   [x] item c
            *   [X] item C
            *   non item
        -   [ ] item 2
        -   [ ] item 3
        """

_base64_md = """
        ## Base 64

        ![picture](../../docs/_static/docs-settings.png)
        """

_admonitions_md = """
        ## Admonitions

        !!! important ""
            This is an admonition box without a title.
        """

_caption_md = """
        ## Caption

        Fruit      | Amount
        ---------- | ------
        Apple      | 20
        Peach      | 10
        Banana     | 3
        Watermelon | 1

        /// caption
        Fruit Count
        ///
        """

_tabs_md = """
        ## Tabs

        /// tab | Tab 1 title
        Tab 1 content
        ///

        /// tab | Tab 2 title
        Tab 2 content
        ///
        """

_details_md = """
        ## Details

        /// details | Basic details
        This is a basic details section
        ///

        /// details | Info details
            type: info

        This shows important information
        ///

        /// details | Warning details  
            type: warn

        This highlights something to watch out for
        ///

        /// details | Danger details
            type: danger

        This indicates a critical warning or dangerous situation
        ///

        /// details | Success details
            type: success

        This indicates a successful outcome or positive note
        ///
        """

_nested_em_md = r"""
        ## Nested em

        This * won't emphasize *

        This *will emphasize*

        ***I'm italic and bold* I am just bold.**

        ***I'm bold and italic!** I am just italic.*
        """

_critic_md = r"""
        ## Critic

        Here is some {--*incorrect*--} Markdown.  I am adding this{++ here++}.  Here is some more {--text
         that I am removing--}text.  And here is even more {++text that I 
         am ++}adding.{~~

        ~>  ~~}Paragraph was deleted and replaced with some spaces.{~~  ~>

        ~~}Spaces were removed and a paragraph was added.

        And here is a comment on {==some
         text==}{>>This works quite well. I just wanted to comment on it.<<}. Substitutions {~~is~>are~~} great!

        General block handling.

        {--

        * test remove
        * test remove
        * test remove
            * test remove
        * test remove

        --}

        {++

        * test add
        * test add
        * test add
            * test add
        * test add

        ++}
        """

_emoji_md = """
        ## Emoji

        :smile: :heart: :thumbsup:
        """

_keys_md = """
        ## Keys

        ++ctrl+alt+delete++
        """

_magic_link_md = """
        ## Magic link

        - Just paste links directly in the document like this: https://google.com.
        - Or even an email address: fake.email@email.com.
        """

_subscripts_md = r"""
        ## Subscripts and strikethrough

        ~~Delete me~~

        CH~3~CH~2~OH

        text~a\ subscript~
        """

__generated_with = "0.15.5"
app = marimo.App(width="medium")


@app.cell
def _(mo):
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    import marimo as mo
    return (mo,)


@app.cell
def _():
    import marimo as mo
    return (mo,)


if __name__ == "__main__":
    app.run()
