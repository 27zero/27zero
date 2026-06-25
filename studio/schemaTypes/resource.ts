import {defineType, defineField} from 'sanity'

export default defineType({
  name: 'resource',
  title: 'Resources',
  type: 'document',
  fields: [
    defineField({
      name: 'title',
      title: 'Title',
      type: 'string',
    }),

    defineField({
      name: 'slug',
      title: 'Slug',
      type: 'slug',
      options: {
        source: 'title',
      },
    }),

    defineField({
      name: 'heroDescription',
      title: 'Hero Description',
      type: 'text',
    }),

    defineField({
      name: 'body',
      title: 'Content',
      type: 'array',
      of: [{type: 'block'}],
    }),
  ],
})
