import type { ReactNode } from 'react'
import { Tab, TabList, TabPanel, Tabs as RACTabs, type Key } from 'react-aria-components'

export interface TabItem {
  id: string
  label: ReactNode
  content: ReactNode
  isDisabled?: boolean
}

export interface TabsProps {
  /** Accessible name of the tab list. */
  label: string
  items: readonly TabItem[]
  selectedKey?: Key
  defaultSelectedKey?: Key
  onSelectionChange?: (key: Key) => void
  /** `automatic` for cheap panels (default); `manual` (Enter/Space) for expensive ones. */
  keyboardActivation?: 'automatic' | 'manual'
}

/** Tabs on React Aria: arrows move, Home/End jump, activation automatic or manual. */
export function Tabs({ label, items, selectedKey, defaultSelectedKey, onSelectionChange, keyboardActivation }: TabsProps) {
  return (
    <RACTabs
      className="ui-tabs"
      selectedKey={selectedKey}
      defaultSelectedKey={defaultSelectedKey}
      onSelectionChange={onSelectionChange}
      keyboardActivation={keyboardActivation}
      disabledKeys={items.filter((i) => i.isDisabled).map((i) => i.id)}
    >
      <TabList className="ui-tabs__list" aria-label={label}>
        {items.map((item) => (
          <Tab key={item.id} id={item.id} className="ui-tabs__tab">
            {item.label}
          </Tab>
        ))}
      </TabList>
      {items.map((item) => (
        <TabPanel key={item.id} id={item.id} className="ui-tabs__panel">
          {item.content}
        </TabPanel>
      ))}
    </RACTabs>
  )
}
